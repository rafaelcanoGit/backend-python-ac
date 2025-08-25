from infrastructure.interfaces.provider_interface import ProviderInterface
from application.services.whatsapp.verify_token_service import VerifyTokenService
from application.services.whatsapp.received_message_service import (
    ReceivedMessageService,
)
from application.services.whatsapp.conversation_service import ConversationService
from application.services.whatsapp.messages_expiration_listener_service import (
    MessagesExpirationListenerService,
)
from application.services.whatsapp.send_message_service import SendMessageService
from application.services.calendar_event.add_calendar_event_service import (
    AddCalendarEventService,
)
from application.services.llm.retreive_user_information_service import (
    RetriveUserInformationService,
)


class ServiceProvider(ProviderInterface):
    """
    ServiceProvider class to manage services thoroughout the application.
    """

    def __init__(self):
        self.services = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        """
        Bind a service provider to a name.
        """
        self.services[name] = callable_fn

    def make(self, name: str):
        """
        Create an instance of the service provider by name.
        """
        if name not in self.services:
            raise Exception(f"Service not found: {name}")
        return self.services[name]()

    def has(self, name: str) -> bool:
        """
        Check if a service provider exists.
        """
        return name in self.services

    # Services registered here will be available in the container
    def register(self, container) -> None:
        """
        Register the service services.
        """
        self.bind("verify_token_service", lambda: VerifyTokenService())

        self.bind(
            "received_message_service",
            lambda: ReceivedMessageService(
                container.make("conversation_service"),
                container.make("whatsapp_repository"),
            ),
        )

        self.bind(
            "conversation_service",
            lambda: ConversationService(container.make("executive_assistant_gpt_4o")),
        )

        self.bind(
            "send_message_service",
            lambda: SendMessageService(container.make("whatsapp_client")),
        )

        self.bind(
            "messages_expiration_listener_service",
            lambda: MessagesExpirationListenerService(
                container.make("redis_connection"),
                container.make("conversation_service"),
                container.make("send_message_service"),
                container.make("builder_state"),
                container.make("langraph_state"),
                container.make("whatsapp_repository"),
            ),
        )

        self.bind(
            "add_calendar_event_service",
            lambda: AddCalendarEventService(container.make("google_calendar_client")),
        )

        self.bind(
            "retreive_user_information_service",
            lambda: RetriveUserInformationService(
                container.make("retriver_assistant_gpt_4o"),
                container.make("whatsapp_repository"),
            ),
        )