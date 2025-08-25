from typing import Any, Dict
from flask import jsonify
from application.interfaces.service_interface import ServiceInterface
from domain.assistants.interfaces.llm_assistant_interface import LlmAssistantInterface
from domain.whatsapp.entities.langraph_state import LangGraphState
from langgraph.graph import StateGraph


class ConversationService(ServiceInterface):
    """
    Service for managing conversations.
    """

    def __init__(self, llm_assistant: LlmAssistantInterface) -> None:
        self.llm_assistant = llm_assistant

    def execute(
        self,
        builder_state: StateGraph,
        langraph_state: LangGraphState,
        user_phone,
        user_message,
    ) -> Dict[str, Any]:
        "Execute the conversation service with the provided user_message."
        return self.init_or_continue_conversation(
            builder_state, langraph_state, user_phone, user_message
        )

    def init_or_continue_conversation(
        self,
        builder_state: StateGraph,
        langraph_state: LangGraphState,
        user_phone: str,
        user_message: str,
    ):
        "Initialize or continue a conversation."
        print(f"🔔 Processing conversation with message: {user_message}", "\n")
        try:
            print(
                "LangGraph State init_or_continue_conversation:", langraph_state, "\n"
            )

            response = self.llm_assistant.invoke(
                builder_state=builder_state,
                langraph_state=langraph_state,
                user_phone=user_phone,
                language="Español",
                user_message=user_message,
            )

            return response
        except Exception as e:
            print(f"An error occurred while processing the conversation: {e}", "\n")
            return f"An error occurred while processing the conversation: {str(e)}"

    def validate(self, *args, **kwargs) -> bool:
        """
        Validate the input for the service.
        """
        # Implement validation logic if necessary
        print("Validating conversation data.")
        return True
