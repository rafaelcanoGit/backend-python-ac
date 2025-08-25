from abc import ABC, abstractmethod


class ProviderInterface(ABC):
    """
    Interface for a container that manages the lifecycle of objects.
    """

    @abstractmethod
    def bind(self, name: str, callable_fn: callable) -> None:
        """
        Bind a name to a callable function.
        """
        pass

    @abstractmethod
    def make(self, name: str):
        """
        Create an instance of the service.
        """
        pass

    @abstractmethod
    def has(self, name: str) -> bool:
        """
        Check if the service exists in the container.
        """
        pass

    @abstractmethod
    def register(self, container) -> None:
        """
        Register the services in the container.
        """
        pass
