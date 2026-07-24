from os import environ as env


class Project:
    def __init__(self):

        self.AI_KEY: str = env.get("AI_KEY", "None")
        self.AI_GATEWAY: str = env.get("AI_GATEWAY", "None")
        self.AI_MODEL = "mimo-v2.5"

        self.RESULT_BASE_PATH = env.get("RESULT_BASE_PATH", "result")

        self.LLM_CONFIG = {
            "model": self.AI_MODEL,
            "api_key": self.AI_KEY,
            "base_url": self.AI_GATEWAY,
            "temperature": 0.6,
            "top_p": 0.95,
        }

        self.BROWSER_PROFILE = {
            "minimum_wait_page_load_time": 0.1,
            "wait_between_actions": 0.1,
            "headless": False,
        }