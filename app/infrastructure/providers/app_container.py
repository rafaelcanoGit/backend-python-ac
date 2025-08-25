from typing import List
from infrastructure.interfaces.provider_interface import ProviderInterface


class AppContainer:
    def __init__(self, providers: List[ProviderInterface]):
        self.providers = providers

    def initialize_services(self) -> None:
        for provider in self.providers:
            provider.register(self)

    def make(self, name: str):
        for provider in self.providers:
            if provider.has(name):
                try:
                    return provider.make(name)
                except Exception as e:
                    print(
                        f"Error al obtener el servicio {name} de {provider.__class__.__name__}: {e}"
                    )
                    raise e
        raise Exception(f"Servicio {name} no encontrado en ningún proveedor.")
