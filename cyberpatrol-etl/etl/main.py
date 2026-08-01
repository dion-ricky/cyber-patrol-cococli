"""Incremental extract/load from the Postgres scanner DB into Snowflake.

Reads new/changed rows from Postgres (watermarked by a timestamp column),
stages them into Snowflake via write_pandas, then MERGEs into the target
tables under CYBERPATROL.RAW. Safe to re-run: MERGE is idempotent and the
watermark only advances after a successful load.

Runs once and exits. Deployed as a standalone Docker container run on a
schedule (see docker-compose.yml) alongside other app infra; connects to
both Postgres and Snowflake as a normal external client using a
programmatic access token for Snowflake auth.

Usage:
    python -m etl.main
"""

import json
import logging
import os
from dataclasses import dataclass, field

import pandas as pd
import psycopg
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TableConfig:
    pg_table: str
    sf_table: str
    pk_cols: list[str]
    watermark_col: str
    columns: list[str]
    json_columns: list[str] = field(default_factory=list)
    timestamp_columns: list[str] = field(default_factory=list)


TABLE_CONFIGS: list[TableConfig] = [
    TableConfig(
        pg_table="scan_requests",
        sf_table="SCAN_REQUESTS",
        pk_cols=["request_id"],
        watermark_col="updated_at",
        columns=["request_id", "status", "error", "created_at", "updated_at"],
        timestamp_columns=["created_at", "updated_at"],
    ),
    TableConfig(
        pg_table="scan_results",
        sf_table="SCAN_RESULTS",
        pk_cols=["id_scrap"],
        watermark_col="created_at",
        columns=[
            "id_scrap",
            "request_id",
            "crawled_time",
            "website",
            "task_id",
            "classify_website",
            "created_at",
        ],
        timestamp_columns=["crawled_time", "created_at"],
    ),
    TableConfig(
        pg_table="urlscan_results",
        sf_table="URLSCAN_RESULTS",
        pk_cols=["id"],
        watermark_col="created_at",
        columns=[
            "id",
            "request_id",
            "uuid",
            "verdicts",
            "page",
            "lists",
            "stats",
            "visible",
            "network_requests",
            "security_details",
            "response_headers",
            "created_at",
        ],
        json_columns=[
            "verdicts",
            "page",
            "lists",
            "stats",
            "visible",
            "network_requests",
            "security_details",
            "response_headers",
        ],
        timestamp_columns=["created_at"],
    ),
]


def connect_snowflake() -> snowflake.connector.SnowflakeConnection:
    """Connect to Snowflake using a programmatic access token (password auth),
    suitable for unattended/headless execution."""
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PAT"],
        role=os.environ.get("SNOWFLAKE_ROLE", "CYBERPATROL_ETL_ROLE"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "CYBERPATROL"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "RAW"),
    )


def get_watermark(sf_conn, table_name: str):
    with sf_conn.cursor() as cur:
        cur.execute(
            "SELECT watermark_value FROM ETL_WATERMARKS WHERE table_name = %s",
            (table_name,),
        )
        row = cur.fetchone()
        return row[0] if row else None


def set_watermark(sf_conn, table_name: str, watermark_col: str, value) -> None:
    with sf_conn.cursor() as cur:
        cur.execute(
            """
            MERGE INTO ETL_WATERMARKS t
            USING (SELECT %s AS table_name, %s AS watermark_col, %s AS watermark_value) s
            ON t.table_name = s.table_name
            WHEN MATCHED THEN UPDATE SET
                watermark_value = s.watermark_value,
                updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT (table_name, watermark_col, watermark_value)
                VALUES (s.table_name, s.watermark_col, s.watermark_value)
            """,
            (table_name, watermark_col, value),
        )


def extract(pg_conn: psycopg.Connection, cfg: TableConfig, watermark) -> pd.DataFrame:
    cols_sql = ", ".join(cfg.columns)
    if watermark is None:
        sql = f"SELECT {cols_sql} FROM {cfg.pg_table} ORDER BY {cfg.watermark_col}"
        params = ()
    else:
        sql = (
            f"SELECT {cols_sql} FROM {cfg.pg_table} "
            f"WHERE {cfg.watermark_col} > %s ORDER BY {cfg.watermark_col}"
        )
        params = (watermark,)
    with pg_conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=cfg.columns)
    for col in cfg.json_columns:
        df[col] = df[col].apply(lambda v: json.dumps(v) if v is not None else None)
    for col in cfg.timestamp_columns:
        df[col] = pd.to_datetime(df[col], utc=True)
    return df


def load(
    sf_conn, cfg: TableConfig, df: pd.DataFrame, database: str, schema: str
) -> int:
    if df.empty:
        return 0

    df.columns = [c.upper() for c in df.columns]
    staging_table = f"{cfg.sf_table}_STAGING"

    with sf_conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {staging_table}")

    write_pandas(
        sf_conn,
        df,
        staging_table,
        database=database,
        schema=schema,
        auto_create_table=True,
        overwrite=True,
        table_type="temporary",
    )

    pk_upper = [c.upper() for c in cfg.pk_cols]
    json_upper = {c.upper() for c in cfg.json_columns}
    all_cols = [c.upper() for c in cfg.columns]

    join_cond = " AND ".join(f"t.{pk} = s.{pk}" for pk in pk_upper)

    def src_expr(col: str) -> str:
        return f"PARSE_JSON(s.{col})" if col in json_upper else f"s.{col}"

    update_set = ", ".join(
        f"{col} = {src_expr(col)}" for col in all_cols if col not in pk_upper
    )
    insert_cols = ", ".join(all_cols)
    insert_vals = ", ".join(src_expr(col) for col in all_cols)

    merge_sql = f"""
        MERGE INTO {cfg.sf_table} t
        USING {staging_table} s
        ON {join_cond}
        WHEN MATCHED THEN UPDATE SET {update_set}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """
    with sf_conn.cursor() as cur:
        cur.execute(merge_sql)
        merged = cur.rowcount
        cur.execute(f"DROP TABLE IF EXISTS {staging_table}")
    return merged


def run() -> None:
    database_url = os.environ["DATABASE_URL"]
    database = os.environ.get("SNOWFLAKE_DATABASE", "CYBERPATROL")
    schema = os.environ.get("SNOWFLAKE_SCHEMA", "RAW")

    with psycopg.connect(database_url) as pg_conn:
        sf_conn = connect_snowflake()
        try:
            for cfg in TABLE_CONFIGS:
                watermark = get_watermark(sf_conn, cfg.sf_table)
                df = extract(pg_conn, cfg, watermark)
                if df.empty:
                    logger.info("%s: no new rows", cfg.pg_table)
                    continue
                merged = load(sf_conn, cfg, df, database, schema)
                watermark_col_upper = cfg.watermark_col.upper()
                new_watermark = df[watermark_col_upper].max()
                set_watermark(sf_conn, cfg.sf_table, cfg.watermark_col, new_watermark)
                sf_conn.commit()
                logger.info(
                    "%s -> %s: merged %d rows, watermark advanced to %s",
                    cfg.pg_table,
                    cfg.sf_table,
                    merged,
                    new_watermark,
                )
        finally:
            sf_conn.close()


if __name__ == "__main__":
    run()
