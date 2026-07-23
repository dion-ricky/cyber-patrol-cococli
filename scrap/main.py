import random
import string
import pandas as pd
import asyncio
from datetime import datetime
from urllib.parse import urlparse
from scrap_general import Scraper


def derive_site_name(link: str) -> str:
    hostname = urlparse(link).hostname or ""
    parts = hostname.split(".")
    if len(parts) > 1:
        parts = parts[:-1]
    return ".".join(parts)


async def process_site(task: str, link: str, scraper, dt: str):
    site_name = derive_site_name(link)
    now = datetime.now()
    scrap_id = f"{site_name}_{now.strftime('%Y%m%d%H%M%S')}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
    timestamp = now.replace(microsecond=now.microsecond // 1000 * 1000)

    info = await scraper.classify_website(link, site_name, scrap_id, timestamp, task)
    result_df = pd.DataFrame([info])
    result_df.to_csv(f"classify_{dt}.csv", index=False)
    print(result_df)


async def main():
    task = "classify"
    link = "https://loginpaypal.statuspage.io/"

    scraper = Scraper()

    dt = datetime.now().strftime("%Y%m%d")
    await process_site(task, link, scraper, dt)


if __name__ == "__main__":
    asyncio.run(main())
