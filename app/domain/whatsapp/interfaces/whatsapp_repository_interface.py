from abc import ABC, abstractmethod


class WhatsappRepositoryInterface(ABC):
    """
    Interface for a repository that provides access to WhatsApp data.
    """

    @abstractmethod
    def get_contact_by_number(self, number: str) -> dict:
        """
        Retrieve user information by their WhatsApp number.

        :param number: The WhatsApp number of the user.
        :return: A dictionary containing the user's information.
        """
        pass

    @abstractmethod
    def save_contact(self, *args, **kwargs) -> None:
        """
        Save WhatsApp data based on provided arguments.
        """
        pass

    @abstractmethod
    def delete_contact(self, *args, **kwargs):
        """
        Delete WhatsApp data based on provided arguments.
        """
        pass

    @abstractmethod
    def add_message_to_buffer(self, *args, **kwargs):
        """
        Add a message to the WhatsApp buffer.
        """
        pass

    @abstractmethod
    def save_message(self, *args, **kwargs):
        """
        Save conversation data.
        """
        pass

    @abstractmethod
    def update_contact_by_id(self, *args, **kwargs):
        """
        Update contact information by ID.
        """
        pass
