from infrastructure.interfaces.provider_interface import ProviderInterface
from langchain_openai import ChatOpenAI
from infrastructure.config.config import get_env


class LLMProvider(ProviderInterface):
    def __init__(self):
        self.llms = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        self.llms[name] = callable_fn

    def make(self, name: str):
        if name not in self.llms:
            raise Exception(f"LLM not found: {name}")
        return self.llms[name]()

    def has(self, name: str) -> bool:
        return name in self.llms

    def register(self, container) -> None:
        self.bind(
            "gpt_4o",
            lambda: ChatOpenAI(
                # model="gpt-4o-mini-2024-07-18",
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=get_env("OPENAI_API_KEY"),
            ),
        )
