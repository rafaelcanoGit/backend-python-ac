from abc import ABC, abstractmethod

class WhatsappClientInterface(ABC):
    @abstractmethod
    def send_message(self, phone_number: str, message: str) -> None:
        """
        Send a message to a WhatsApp user.

        :param phone_number: The WhatsApp phone number of the user.
        :param message: The message to be sent.
        """
        pass