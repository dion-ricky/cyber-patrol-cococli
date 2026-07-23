import csv
import time
from pathlib import Path

from google_play_scraper import app as gp_app
from google_play_scraper import search as gp_search
from google_play_scraper.exceptions import NotFoundError

KEYWORDS_FILE = Path(__file__).parent / "keyword_scrap.txt"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "playstore_apps.csv"

LANG = "id"
COUNTRY = "id"
SEARCH_N_HITS = 30
SEARCH_SLEEP = 0.5
DETAIL_SLEEP = 0.3

CSV_COLUMNS = [
    "nama_aplikasi",
    "developer",
    "developerId",
    "developerEmail",
    "developerWebsite",
    "developerAddress",
    "score",
    "ratings",
    "reviews",
    "installs",
    "categories",
    "appId",
    "url",
    "country",
    "matched_keyword",
]


def load_keywords(path: Path) -> list[str]:
    keywords = []
    for line in path.read_text(encoding="utf-8").splitlines():
        field = line.split("\t")[-1].strip()
        if field:
            keywords.append(field)
    return keywords


def search_apps(keywords: list[str]) -> dict[str, set[str]]:
    app_keywords: dict[str, set[str]] = {}
    total = len(keywords)
    for i, keyword in enumerate(keywords, start=1):
        try:
            results = gp_search(keyword, lang=LANG, country=COUNTRY, n_hits=SEARCH_N_HITS)
        except Exception as exc:
            print(f'[{i}/{total}] "{keyword}" -> ERROR: {exc}')
            continue
        for result in results:
            app_id = result.get("appId")
            if not app_id:
                continue
            app_keywords.setdefault(app_id, set()).add(keyword)
        print(f'[{i}/{total}] "{keyword}" -> {len(results)} hits (total unique so far: {len(app_keywords)})')
        time.sleep(SEARCH_SLEEP)
    return app_keywords


def fetch_details(app_keywords: dict[str, set[str]]) -> list[dict]:
    rows = []
    app_ids = sorted(app_keywords)
    total = len(app_ids)
    for i, app_id in enumerate(app_ids, start=1):
        try:
            details = gp_app(app_id, lang=LANG, country=COUNTRY)
        except NotFoundError:
            print(f"[{i}/{total}] {app_id} -> NOT FOUND, skipped")
            continue
        except Exception as exc:
            print(f"[{i}/{total}] {app_id} -> ERROR: {exc}, skipped")
            continue

        categories = "; ".join(
            c.get("name", "") for c in details.get("categories", []) if c.get("name")
        )

        rows.append(
            {
                "nama_aplikasi": details.get("title"),
                "developer": details.get("developer"),
                "developerId": details.get("developerId"),
                "developerEmail": details.get("developerEmail"),
                "developerWebsite": details.get("developerWebsite"),
                "developerAddress": details.get("developerAddress"),
                "score": details.get("score"),
                "ratings": details.get("ratings"),
                "reviews": details.get("reviews"),
                "installs": details.get("installs"),
                "categories": categories,
                "appId": details.get("appId"),
                "url": details.get("url"),
                "country": "Indonesia",
                "matched_keyword": ", ".join(sorted(app_keywords[app_id])),
            }
        )
        print(f"[{i}/{total}] {app_id} -> OK ({details.get('title')})")
        time.sleep(DETAIL_SLEEP)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    keywords = load_keywords(KEYWORDS_FILE)
    print(f"Loaded {len(keywords)} keywords from {KEYWORDS_FILE.name}")

    app_keywords = search_apps(keywords)
    print(f"\nFound {len(app_keywords)} unique app IDs across all keywords\n")

    rows = fetch_details(app_keywords)
    write_csv(rows, OUTPUT_FILE)

    print(
        f"\nDone. Keywords processed: {len(keywords)}, "
        f"unique apps found: {len(app_keywords)}, "
        f"rows written: {len(rows)}\n"
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
