from project import Project
from browser_use import Agent, ChatOpenAI, BrowserProfile

class AIScrapper:
    def __init__(self):
        self.config = Project()

    # =========================
    # RUN AGENT
    # =========================
    async def run_agent(self, task):
        llm = ChatOpenAI(**self.config.LLM_CONFIG)
        browser_profile = BrowserProfile(**self.config.BROWSER_PROFILE)
        
        # task_qris = self.create_task_qris(website, username, password)
        # task_phone = self.create_task_phone_number(website, username, password)

        agent = Agent(
            task=task,
            llm=llm,
            browser_profile=browser_profile,
            # use_vision=False,
            # disable_observability=True,
            # max_input_tokens=30000,
            # save_conversation_path=None
        )
        history = await agent.run(max_steps=99)
        
        return history