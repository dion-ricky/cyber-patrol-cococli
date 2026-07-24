from typing import Any

from browser_use import Agent, BrowserProfile, ChatOpenAI

from config.settings import Settings


class BrowserAgent:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def run(self, task: str) -> Any:
        llm = ChatOpenAI(**self._settings.llm.to_dict())
        browser_profile = BrowserProfile(**self._settings.browser.to_dict())

        agent = Agent(
            task=task,
            llm=llm,
            browser_profile=browser_profile,
        )
        return await agent.run(max_steps=99)
