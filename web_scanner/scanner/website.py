import os
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import Settings
from models.scan import ScanResult
from prompts.classify import build_classify_prompt
from scanner.browser import BrowserAgent
from utils.url import derive_site_name, generate_scrap_id


class WebsiteScanner:
    def __init__(self, browser: BrowserAgent, settings: Settings) -> None:
        self._browser = browser
        self._settings = settings

    async def scan(self, url: str) -> ScanResult:
        site_name = derive_site_name(url)
        scrap_id = generate_scrap_id(site_name)
        timestamp = datetime.now().replace(microsecond=0)

        prompt = build_classify_prompt(url)
        history = await self._browser.run(prompt)

        classification = self._extract_result(history)
        screenshot = self._read_screenshot(history)

        return ScanResult(
            scrap_id=scrap_id,
            crawled_time=timestamp,
            website=site_name,
            task_id=prompt,
            classification=classification,
            screenshot=screenshot,
        )

    @staticmethod
    def _extract_result(history: Any) -> str:
        result = history.final_result()
        return str(result) if result else "UNKNOWN"

    @staticmethod
    def _read_screenshot(history: Any) -> bytes | None:
        screenshot_paths = history.screenshot_paths()
        if not screenshot_paths:
            return None

        last_path = screenshot_paths[-1]
        if last_path and os.path.exists(last_path):
            return Path(last_path).read_bytes()
        return None
