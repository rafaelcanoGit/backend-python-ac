from infrastructure.interfaces.provider_interface import ProviderInterface
from domain.assistants.entities.executive_assistant import ExecutiveAssistant
from domain.assistants.entities.retriver_assistant import RetriverAssistant
from langchain_openai import OpenAIEmbeddings

# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from domain.whatsapp.entities.langraph_state import LangGraphState
from langgraph.graph import StateGraph
from domain.whatsapp.entities.chat_state import ChatState

from infrastructure.config.config import get_env


class AssistantProvider(ProviderInterface):
    def __init__(self):
        self.assistants = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        self.assistants[name] = callable_fn

    def make(self, name: str):
        if name not in self.assistants:
            raise Exception(f"LLM not found: {name}")
        return self.assistants[name]()

    def has(self, name: str) -> bool:
        return name in self.assistants

    # Assistants registrated in the provider
    def register(self, container) -> None:
        self.bind(
            "executive_assistant_gpt_4o",
            lambda: ExecutiveAssistant(),
        )

        self.bind(
            "retriver_assistant_gpt_4o",
            lambda: RetriverAssistant(
                container.make("gpt_4o"),
            ),
        )

        persist_directory = get_env("CHROMA_PERSIST_DIRECTORY", "chroma_data_dev")
        self.bind(
            "langraph_state",
            lambda: LangGraphState(
                container.make("gpt_4o"),
                Chroma(
                    collection_name="executive_assistant_memories_gpt_4o",
                    persist_directory=f"./{persist_directory}",
                    embedding_function=OpenAIEmbeddings(),
                ),
                container.make("google_calendar_client"),
                container.make("whatsapp_repository"),
            ),
        )

        self.bind("builder_state", lambda: self.make_state_graph())

    def make_state_graph(self):
        graph = StateGraph(ChatState)
        graph.state_type = ChatState
        return graph
