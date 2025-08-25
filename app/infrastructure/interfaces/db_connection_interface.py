from abc import ABC, abstractmethod


class DBConnectionInterface(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the database."""
        pass

    @abstractmethod
    def get_connection(self):
        """Get the current database connection."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        pass
