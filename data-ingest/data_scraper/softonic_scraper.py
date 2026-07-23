import csv
import random
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Page, sync_playwright

SOURCE_CSV = Path(__file__).parent.parent / "daftar_pinjaman_online_ilegal.csv"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "softonic_apps.csv"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
NAV_TIMEOUT_MS = 30_000
MAX_RETRIES = 3
DELAY_RANGE = (8.0, 15.0)

CSV_COLUMNS = [
    "url",
    "nama_aplikasi",
    "developer",
    "developer_url",
    "category",
    "score",
    "votes",
    "downloads_softonic",
    "version",
    "latest_update",
    "os_requirement",
    "language",
    "license",
    "download_option",
    "status",
]

WEBDRIVER_MASK_SCRIPT = (
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)


def load_softonic_urls(path: Path) -> list[str]:
    urls = []
    seen = set()
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = row.get("url", "").strip()
            if "softonic" in urlparse(url).netloc and url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def new_page(context) -> Page:
    page = context.new_page()
    page.add_init_script(WEBDRIVER_MASK_SCRIPT)
    return page


def is_blocked(page: Page) -> bool:
    title = page.title()
    if "client challenge" in title.lower():
        return True
    if page.query_selector("h1") is None:
        return True
    return False


def spec_value(page: Page, label: str) -> str:
    node = page.query_selector(f"xpath=//h3[normalize-space(text())='{label}']/following-sibling::*[1]")
    return node.inner_text().strip() if node else ""


def extract(page: Page, url: str) -> dict:
    h1 = page.query_selector("h1")
    nama = h1.inner_text().replace("\xa0", " ").strip() if h1 else ""
    nama = re.sub(r"\s+for (Android|iOS|Windows|Mac)$", "", nama)

    dev_node = page.query_selector(
        "xpath=//h3[normalize-space(text())='Developer']/following-sibling::*[1]//a"
    )
    developer = dev_node.inner_text().strip() if dev_node else ""
    developer_url = dev_node.get_attribute("href") if dev_node else ""

    crumbs = page.query_selector_all("nav[aria-label='Breadcrumb'] li a")
    crumb_texts = [c.inner_text().strip() for c in crumbs]
    category = " > ".join(t for t in crumb_texts if t and t.lower() != "home")

    rating_node = page.query_selector("[aria-label*='Rated'][aria-label*='stars']")
    score = ""
    if rating_node:
        m = re.search(r"Rated ([\d.]+) stars", rating_node.get_attribute("aria-label") or "")
        if m:
            score = m.group(1)

    votes_node = page.query_selector("[aria-label*='votes']")
    votes = ""
    if votes_node:
        m = re.search(r"(\d+)\s*votes", votes_node.get_attribute("aria-label") or "")
        if m:
            votes = m.group(1)

    return {
        "url": url,
        "nama_aplikasi": nama,
        "developer": developer,
        "developer_url": developer_url or "",
        "category": category,
        "score": score,
        "votes": votes,
        "downloads_softonic": spec_value(page, "Downloads"),
        "version": spec_value(page, "Version"),
        "latest_update": spec_value(page, "Latest update"),
        "os_requirement": spec_value(page, "OS"),
        "language": spec_value(page, "Language"),
        "license": spec_value(page, "License"),
        "download_option": spec_value(page, "Download Options"),
    }


def scrape_one(context, url: str) -> dict:
    last_status = "error"
    for attempt in range(1, MAX_RETRIES + 1):
        page = new_page(context)
        try:
            resp = page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
            status_code = resp.status if resp else None

            if status_code == 404:
                page.close()
                return {"url": url, "status": "not_found"}

            if status_code is None or status_code >= 400 or is_blocked(page):
                last_status = "blocked"
                page.close()
                time.sleep(2 * attempt)
                continue

            row = extract(page, url)
            row["status"] = "ok"
            page.close()
            return row
        except Exception as exc:
            last_status = "error"
            print(f"    attempt {attempt} error: {exc}")
            page.close()
            time.sleep(2 * attempt)

    return {"url": url, "status": last_status}


def load_done_urls(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as f:
        return {row["url"]: row for row in csv.DictReader(f)}


def main() -> None:
    urls = load_softonic_urls(SOURCE_CSV)
    print(f"Loaded {len(urls)} softonic.com URLs from {SOURCE_CSV.name}")

    done = load_done_urls(OUTPUT_FILE)
    already_ok = {u for u, r in done.items() if r.get("status") == "ok"}
    todo = [u for u in urls if u not in already_ok]
    print(f"Already OK from a previous run: {len(already_ok)}. Remaining to fetch: {len(todo)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    is_new_file = not OUTPUT_FILE.exists()
    out_f = OUTPUT_FILE.open("a" if not is_new_file else "w", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(out_f, fieldnames=CSV_COLUMNS)
    if is_new_file:
        writer.writeheader()

    from collections import Counter

    counts = Counter(r.get("status", "") for r in done.values() if r["url"] not in todo)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--headless=new"])
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        total = len(todo)
        for i, url in enumerate(todo, start=1):
            row = scrape_one(context, url)
            writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})
            out_f.flush()
            counts[row["status"]] += 1
            print(f"[{i}/{total}] {url} -> {row['status']}")
            time.sleep(random.uniform(*DELAY_RANGE))

        browser.close()

    out_f.close()
    print(f"\nDone. Status breakdown (cumulative): {dict(counts)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
