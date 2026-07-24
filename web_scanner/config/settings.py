from dataclasses import dataclass, field
from functools import lru_cache
from os import environ as env


@dataclass(frozen=True)
class LLMConfig:
    model: str = "mimo-v2.5"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.6
    top_p: float = 0.95

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }


@dataclass(frozen=True)
class BrowserConfig:
    minimum_wait_page_load_time: float = 0.1
    wait_between_actions: float = 0.1
    headless: bool = False

    def to_dict(self) -> dict:
        return {
            "minimum_wait_page_load_time": self.minimum_wait_page_load_time,
            "wait_between_actions": self.wait_between_actions,
            "headless": self.headless,
        }


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = ""

    def to_dict(self) -> dict:
        return {
            "url": self.url,
        }


@dataclass(frozen=True)
class Settings:
    llm: LLMConfig = field(default_factory=LLMConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)

    @classmethod
    def from_env(cls) -> "Settings":
        headless = env.get("HEADLESS", "true").lower() == "true"
        return cls(
            llm=LLMConfig(
                api_key=env.get("AI_KEY", ""),
                base_url=env.get("AI_GATEWAY", ""),
            ),
            browser=BrowserConfig(headless=headless),
            db=DatabaseConfig(
                url=env.get("DATABASE_URL", ""),
            ),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
