import re
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).parent
UP_MARKER = "-- UP"
DOWN_MARKER = "-- DOWN"

TRACKING_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _ensure_tracking_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(TRACKING_TABLE_SQL)
    conn.commit()


def _get_applied_versions(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version")
        return {row[0] for row in cur.fetchall()}


def _discover_migrations() -> list[tuple[str, Path]]:
    migrations = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = re.match(r"^(\d+)_", path.name)
        if match:
            version = match.group(1)
            migrations.append((version, path))
    return migrations


def _extract_up_sql(path: Path) -> str:
    content = path.read_text()
    up_start = content.index(UP_MARKER) + len(UP_MARKER)
    down_pos = content.find(DOWN_MARKER)
    if down_pos != -1:
        return content[up_start:down_pos].strip()
    return content[up_start:].strip()


def run_migrations(conn: psycopg.Connection) -> list[str]:
    _ensure_tracking_table(conn)
    applied = _get_applied_versions(conn)
    discovered = _discover_migrations()

    newly_applied = []
    for version, path in discovered:
        if version in applied:
            continue

        sql = _extract_up_sql(path)
        print(f"Applying migration {version}: {path.name}")
        with conn.cursor() as cur:
            cur.execute(sql)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (version,),
            )
        conn.commit()
        newly_applied.append(version)
        print(f"  Applied {version}")

    if not newly_applied:
        print("No pending migrations")

    return newly_applied
