import argparse
import asyncio
from datetime import datetime

import pandas as pd

from config.settings import get_settings
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
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output CSV filename. Defaults to classify_YYYYMMDD.csv.",
    )
    return parser.parse_args()


def write_results(results: list[dict], output_path: str) -> None:
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    print(df.to_string(index=False))


async def main() -> None:
    args = parse_args()
    settings = get_settings()

    browser = BrowserAgent(settings)
    scanner = WebsiteScanner(browser, settings)

    results = []
    for url in args.urls:
        print(f"Scanning: {url}")
        result = await scanner.scan(url)
        results.append(result.to_dict())
        print(f"  -> {result.classification}")

    date_str = datetime.now().strftime("%Y%m%d")
    output_path = args.output or f"classify_{date_str}.csv"
    write_results(results, output_path)


if __name__ == "__main__":
    asyncio.run(main())
