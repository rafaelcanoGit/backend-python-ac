from abc import ABC, abstractmethod
from typing import Any, Dict


class ServiceInterface(ABC):
    """
    Interface for a service that provides business logic.
    """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the service logic and return a JSON-like dictionary.
        """
        pass

    @abstractmethod
    def validate(self, *args, **kwargs):
        """
        Validate the input for the service.
        """
        pass
