from abc import ABC, abstractmethod


class LlmAssistantInterface(ABC):

    @abstractmethod
    def initialize_assistant(self) -> None:
        """
        Initialize the LLM assistant with necessary parameters.
        """
        pass

    @abstractmethod
    def invoke(self, *args, **kwargs) -> dict:
        """
        Invoke the LLM assistant with a given prompt.
        """
        pass
