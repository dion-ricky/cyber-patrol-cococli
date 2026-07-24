import os
import shutil
from datetime import datetime
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
        self._save_screenshots(history, scrap_id)

        return ScanResult(
            scrap_id=scrap_id,
            crawled_time=timestamp,
            website=site_name,
            task_id=prompt,
            classification=classification,
        )

    @staticmethod
    def _extract_result(history: Any) -> str:
        result = history.final_result()
        return str(result) if result else "UNKNOWN"

    def _save_screenshots(self, history: Any, scrap_id: str) -> None:
        screenshot_paths = history.screenshot_paths()
        if not screenshot_paths:
            return

        output_dir = self._settings.result_base_path
        os.makedirs(output_dir, exist_ok=True)

        last_path = screenshot_paths[-1]
        if last_path and os.path.exists(last_path):
            dst = os.path.join(output_dir, f"{scrap_id}_final.png")
            shutil.copy2(last_path, dst)
