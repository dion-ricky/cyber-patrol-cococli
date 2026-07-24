import argparse
import asyncio

from config.settings import get_settings
from db.connection import get_connection
from db.repository import ensure_schema, insert_scan_result
from scanner.browser import BrowserAgent
from scanner.website import WebsiteScanner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify websites using AI-powered browser automation."
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more URLs to classify.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    settings = get_settings()

    conn = get_connection(settings)
    ensure_schema(conn)

    browser = BrowserAgent(settings)
    scanner = WebsiteScanner(browser, settings)

    for url in args.urls:
        print(f"Scanning: {url}")
        result = await scanner.scan(url)
        insert_scan_result(conn, result)
        print(f"  -> {result.classification} (saved to DB)")

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
