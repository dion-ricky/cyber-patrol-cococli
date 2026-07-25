import asyncio
import sys

from config.settings import get_settings
from db.connection import get_connection
from db.migrations.runner import run_migrations
from db.repository import insert_scan_result, update_scan_status
from scanner.browser import BrowserAgent
from scanner.website import WebsiteScanner


async def scan_url(request_id: str, url: str) -> None:
    settings = get_settings()
    conn = get_connection(settings)
    run_migrations(conn)

    try:
        update_scan_status(conn, request_id, "in_progress")

        browser = BrowserAgent(settings)
        scanner = WebsiteScanner(browser, settings)
        result = await scanner.scan(url)

        insert_scan_result(conn, result, request_id)
        update_scan_status(conn, request_id, "done")
    except Exception as e:
        update_scan_status(conn, request_id, "failed", error=str(e))
        raise
    finally:
        conn.close()


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: scan_worker.py <request_id> <url>", file=sys.stderr)
        sys.exit(1)

    request_id = sys.argv[1]
    url = sys.argv[2]
    asyncio.run(scan_url(request_id, url))


if __name__ == "__main__":
    main()
