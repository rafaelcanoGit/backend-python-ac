from infrastructure.interfaces.provider_interface import ProviderInterface
from infrastructure.repositories.whatsapp_repository import WhatsappRepository


class RepositoryProvider(ProviderInterface):

    def __init__(self):
        self.repositories = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        self.repositories[name] = callable_fn

    def make(self, name: str):
        if name not in self.repositories:
            raise Exception(f"Repository not found: {name}")
        return self.repositories[name]()

    def has(self, name: str) -> bool:
        return name in self.repositories

    def register(self, container) -> None:
        self.bind(
            "whatsapp_repository",
            lambda: WhatsappRepository(
                container.make("backend_ac_client"),
                container.make("redis_connection")
            ),
        )
