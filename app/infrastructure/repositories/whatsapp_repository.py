from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)
from infrastructure.interfaces.db_connection_interface import DBConnectionInterface
from infrastructure.interfaces.backend_ac_client_interface import (
    BackendACClientInterface,
)
from flask import jsonify
import pymysql
import json


class WhatsappRepository(WhatsappRepositoryInterface):

    def __init__(
        self,
        backend_ac_client: BackendACClientInterface,
        redis_connection: DBConnectionInterface,
    ) -> None:
        """
        Initialize the WhatsappRepository with a database connection.
        """
        self.backend_ac_client = backend_ac_client
        self.redis_connection = redis_connection
        self.init_connections()

    def init_connections(self) -> None:
        """
        Initialize the database and Redis connections.
        """
        if not self.redis_connection.is_connected():
            self.redis_connection.connect()

    def close_connections(self) -> None:
        """
        Close the database and Redis connections.
        """

        if self.redis_connection.is_connected():
            self.redis_connection.disconnect()

    def __del__(self):
        """
        Destructor to close the database connection when the repository is destroyed.
        """
        self.close_connections()

    # 1.
    def get_contact_by_number(self, number: str) -> dict:
        """
        Retrieve user information by their WhatsApp number.

        :param number: The WhatsApp number of the user.
        :return: A dictionary containing the user's information.
        """

        try:
            result = self.backend_ac_client.get_contact_by_number(number)

            if result:
                return {
                    "id": result["id"],
                    "phone_number": result["phone_number"],
                    "created_at": result["created_at"],
                    "updated_at": result["updated_at"],
                }
            else:
                return None

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return None

    # 2.
    def save_contact(self, number: str) -> dict:
        """
        Save user information in the WhatsApp database and return the created user.

        :param number: The WhatsApp number of the user.
        :return: A dictionary with the created user's information.
        """
        try:
            user = self.backend_ac_client.save_contact(number)
            print(f"** User {number} saved successfully. ✅", "User:", user, "\n")

            # Return the created user as a dictionary.
            if user:
                return {
                    "id": user["id"],
                    "phone_number": user["phone_number"],
                    "created_at": user["created_at"],
                    "updated_at": user["updated_at"],
                }
        except pymysql.MySQLError as e:
            print(f"Error saving user {number}: {e}")

    # 3.
    def delete_contact(self, number: str) -> None:
        """
        Delete WhatsApp data for a given user ID.
        :param user_id: The ID of the user whose WhatsApp data is to be deleted.
        """

    # 5.
    def update_contact_by_id(
        self, contact_id: int, column_to_update: str, new_value: str
    ) -> None:
        """
        Update a specific column of a contact by its ID.
        :param contact_id: The ID of the contact to update.
        :param column_to_update: The column to update (e.g., "phone_number").
        :param new_value: The new value to set for the column.
        """
        try:
            self.backend_ac_client.update_contact_by_id(
                contact_id, column_to_update, new_value
            )

            print(
                f"\n ** Contact with ID {contact_id} updated successfully ✅. '{column_to_update}' set to {new_value}.",
                "\n",
            )
        except pymysql.MySQLError as e:
            print(f"Error updating contact with ID {contact_id}: {e}")

    # 6.
    def save_message(
        self,
        user: dict,
        type_sender: str,
        message: dict,
    ) -> None:
        """
        Save a conversation between a user and the system.

        :param user: The user's phone number.
        :param type_sender: The type of sender (e.g., "USER", "SYSTEM").
        :param message: The user's message.
        """
        try:
            self.backend_ac_client.save_message(user["id"], type_sender, message)

            print(
                f"** Conversación guardada con éxito ✅ para {user['phone_number']}. Message: {message} ✅",
                "\n",
            )

        except pymysql.MySQLError as e:
            print(f"Error saving conversation for {user}: {e}")

    def add_message_to_buffer(self, user: str, message: str) -> None:
        list_key = f"whatsapp:buffer:{user}"
        self.redis_connection.get_connection().rpush(list_key, message)

        timer_key = f"whatsapp:timer:{user}"
        self.redis_connection.get_connection().set(
            timer_key, "true", ex=30
        )  # "true" es simplemente un placeholder, no tiene significado semántico; solo necesitamos que la clave exista para que pueda expirar.
        print(f"Mensaje añadido al buffer de {user}: {message}", "\n")
        print(
            f"Buffer actual para {user}: {self.redis_connection.get_connection().lrange(list_key, 0, -1)}",
            "\n",
        )
