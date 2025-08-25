from domain.assistants.interfaces.llm_assistant_interface import LlmAssistantInterface
from application.interfaces.service_interface import ServiceInterface
from typing import Any, Dict
from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)


class RetriveUserInformationService(ServiceInterface):

    def __init__(
        self,
        retriver_assistant: LlmAssistantInterface,
        whatsapp_repository: WhatsappRepositoryInterface,
    ) -> None:
        """ """
        self.retriver_assistant = retriver_assistant
        self.whatsapp_repository = whatsapp_repository

    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the service logic to add a calendar event.
        :param args: Positional arguments for the service.
        :param kwargs: Keyword arguments for the service.
        :return: A dictionary containing the result of the operation.
        """
        try:
            conversation = kwargs.get("conversation")
            telefono = kwargs.get("telefono", "0000000000")
            response = self.retriver_assistant.invoke(conversation=conversation, telefono=telefono)

            return response
        except Exception as e:
            print(f"An error occurred while processing the conversation: {e}", "\n")
            return f"An error occurred while processing the conversation: {str(e)}"

    def validate(self, *args, **kwargs):
        """
        Validate the service parameters.
        """
        return super().validate(*args, **kwargs)
