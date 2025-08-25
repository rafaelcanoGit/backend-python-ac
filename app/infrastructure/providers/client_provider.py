from infrastructure.interfaces.provider_interface import ProviderInterface
from infrastructure.clients.whatsapp_client import WhatsappClient
from infrastructure.clients.google_calendar_client import GoogleCalendarClient
from infrastructure.clients.backend_ac_client import BackendACClient
from infrastructure.config.config import get_env


class ClientProvider(ProviderInterface):
    def __init__(self):
        self.clients = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        self.clients[name] = callable_fn

    def make(self, name: str):
        if name not in self.clients:
            raise Exception(f"Client not found: {name}")
        return self.clients[name]()

    def has(self, name: str) -> bool:
        return name in self.clients

    def register(self, container) -> None:
        self.bind(
            "whatsapp_client",
            lambda: WhatsappClient(
                get_env("WHATSAPP_API_URL", "https://api.whatsapp.com"),
                get_env("WHATSAPP_TOKEN", "your_api_key_here"),
            ),
        )

        webhook_google_calendar = "https://0497256c184f.ngrok-free.app" + get_env(
            "GOOGLE_CALENDAR_WEBHOOK", "/webhook/google-calendar"
        )

        self.bind(
            "google_calendar_client",
            lambda: GoogleCalendarClient(
                container.make("whatsapp_repository"),
                webhook_url=webhook_google_calendar,
            ),
        )

        self.bind(
            "backend_ac_client",
            lambda: BackendACClient(
                get_env("BACKEND_AC_API_URL", "https://api.backendac.com"),
                get_env("BACKEND_AC_API_KEY", "your_backend_ac_api_key_here"),
            ),
        )
