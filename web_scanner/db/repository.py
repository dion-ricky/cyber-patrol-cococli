import psycopg

from models.scan import ScanResult

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scan_results (
    id_scrap        TEXT PRIMARY KEY,
    crawled_time    TIMESTAMPTZ NOT NULL,
    website         TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    classify_website TEXT NOT NULL,
    screenshot      BYTEA,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
    conn.commit()


def insert_scan_result(conn: psycopg.Connection, result: ScanResult) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scan_results
                (id_scrap, crawled_time, website, task_id,
                 classify_website, screenshot)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_scrap) DO UPDATE SET
                crawled_time = EXCLUDED.crawled_time,
                website = EXCLUDED.website,
                task_id = EXCLUDED.task_id,
                classify_website = EXCLUDED.classify_website,
                screenshot = EXCLUDED.screenshot
            """,
            (
                result.scrap_id,
                result.crawled_time,
                result.website,
                result.task_id,
                result.classification,
                result.screenshot,
            ),
        )
    conn.commit()
