from task_creation import TaskCreation
from ai_scrapper import AIScrapper
from datetime import datetime
from project import Project
import os
import shutil


class Scraper:
    def __init__(self) -> None:
        self.run_datetime = datetime.now()
        self.task_creator = TaskCreation()
        self.ai = AIScrapper()
        self.config = Project()

    async def classify_website(
        self, website: str, domain: str, id_scrap: str, timestamp: str, task: str
    ) -> dict:
        task = self.task_creator.classify_website(website)

        history = await self.ai.run_agent(task)
        result_text = str(
            history.final_result()
            if callable(history.final_result)
            else history.final_result
        )

        print(history.errors())
        screenshot_paths = history.screenshot_paths()
        picture_dir = os.path.join(self.config.RESULT_BASE_PATH)
        os.makedirs(picture_dir, exist_ok=True)

        screenshot_map = {}
        if screenshot_paths and len(screenshot_paths) > 0:
            for idx, src in enumerate(screenshot_paths):
                if src is not None and os.path.exists(src):
                    if src == screenshot_paths[-1]:
                        dst_filename = f"{id_scrap}_{idx}.png"
                        dst_path = os.path.join(picture_dir, dst_filename)
                        shutil.copy2(src, dst_path)
                        screenshot_map[idx] = dst_path

        info = {
            "id_scrap": id_scrap,
            "crawled_time": timestamp,
            "website": domain,
            "task_id": task,
            "classify_website": result_text,
        }

        return info
