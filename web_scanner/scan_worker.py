import asyncio
import logging
import sys

from config.settings import get_settings
from db.connection import get_connection
from db.migrations.runner import run_migrations
from db.repository import insert_scan_result, insert_urlscan_result, update_scan_status
from scanner.browser import BrowserAgent
from scanner.urlscan import UrlScanClient, UrlScanData
from scanner.website import WebsiteScanner

logger = logging.getLogger(__name__)


async def scan_url(request_id: str, url: str) -> None:
    settings = get_settings()
    conn = get_connection(settings)
    run_migrations(conn)

    try:
        update_scan_status(conn, request_id, "in_progress")

        browser = BrowserAgent(settings)
        scanner = WebsiteScanner(browser, settings)

        browser_task = scanner.scan(url)

        urlscan_task = None
        if settings.urlscan_api_key:
            client = UrlScanClient(settings.urlscan_api_key)
            urlscan_task = _safe_urlscan(client, url)

        if urlscan_task:
            results = await asyncio.gather(browser_task, urlscan_task)
            browser_result = results[0]
            urlscan_result = results[1]
        else:
            browser_result = await browser_task
            urlscan_result = None

        insert_scan_result(conn, browser_result, request_id)

        if urlscan_result:
            insert_urlscan_result(conn, urlscan_result, request_id)

        update_scan_status(conn, request_id, "done")
    except Exception as e:
        update_scan_status(conn, request_id, "failed", error=str(e))
        raise
    finally:
        conn.close()


async def _safe_urlscan(client: UrlScanClient, url: str) -> UrlScanData | None:
    try:
        return await client.scan(url)
    except Exception:
        logger.exception("urlscan.io failed for %s, continuing without it", url)
        return None


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: scan_worker.py <request_id> <url>", file=sys.stderr)
        sys.exit(1)

    request_id = sys.argv[1]
    url = sys.argv[2]
    asyncio.run(scan_url(request_id, url))


if __name__ == "__main__":
    main()
