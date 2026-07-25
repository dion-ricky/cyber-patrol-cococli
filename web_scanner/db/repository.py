import psycopg

from models.scan import ScanResult


def create_scan_request(conn: psycopg.Connection, request_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO scan_requests (request_id, status) VALUES (%s, 'pending')",
            (request_id,),
        )
    conn.commit()


def update_scan_status(
    conn: psycopg.Connection,
    request_id: str,
    status: str,
    error: str | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE scan_requests
            SET status = %s, error = %s, updated_at = NOW()
            WHERE request_id = %s
            """,
            (status, error, request_id),
        )
    conn.commit()


def insert_scan_result(
    conn: psycopg.Connection, result: ScanResult, request_id: str
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scan_results
                (id_scrap, request_id, crawled_time, website, task_id,
                 classify_website, screenshot)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_scrap) DO UPDATE SET
                request_id = EXCLUDED.request_id,
                crawled_time = EXCLUDED.crawled_time,
                website = EXCLUDED.website,
                task_id = EXCLUDED.task_id,
                classify_website = EXCLUDED.classify_website,
                screenshot = EXCLUDED.screenshot
            """,
            (
                result.scrap_id,
                request_id,
                result.crawled_time,
                result.website,
                result.task_id,
                result.classification,
                result.screenshot,
            ),
        )
    conn.commit()


def get_scan_request(conn: psycopg.Connection, request_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT request_id, status, error, created_at, updated_at
            FROM scan_requests
            WHERE request_id = %s
            """,
            (request_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "request_id": row[0],
            "status": row[1],
            "error": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }


def get_scan_results_by_request(
    conn: psycopg.Connection, request_id: str
) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_scrap, crawled_time, website, task_id, classify_website
            FROM scan_results
            WHERE request_id = %s
            """,
            (request_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "id_scrap": row[0],
                "crawled_time": row[1],
                "website": row[2],
                "task_id": row[3],
                "classify_website": row[4],
            }
            for row in rows
        ]
