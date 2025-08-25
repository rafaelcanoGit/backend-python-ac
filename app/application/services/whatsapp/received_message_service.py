from application.interfaces.service_interface import ServiceInterface
from typing import Any, Dict
from flask import jsonify
from domain.whatsapp.helpers.wp_helper import (
    get_data_user,
    get_message_user,
    get_number_user,
)
from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)


class ReceivedMessageService(ServiceInterface):
    """
    Service for processing received messages.
    """

    def __init__(
        self,
        conversation_service: ServiceInterface,
        whatsapp_repository: WhatsappRepositoryInterface,
    ) -> None:
        self.conversation_service = conversation_service
        self.whatsapp_repository = whatsapp_repository

    def execute(
        self,
        data: dict,
    ) -> Dict[str, Any]:
        """
        Process the received message data.
        """
        try:
            data_user = get_data_user(data)
            message = get_message_user(data_user["type"], data_user)
            number = get_number_user(data_user)

            user = self.whatsapp_repository.get_contact_by_number(number)
            
            if user:
                print(f"User found: ✅ {user}", "\n")

            if not user:
                user = self.whatsapp_repository.save_contact(number)
                print(f"New user created: ✅ {user}", "\n")

            self.whatsapp_repository.add_message_to_buffer(number, message)

            return (
                jsonify(
                    {
                        "message": f"Mensaje: '{message}' recibido con éxito. ✅",
                        "status": 200,
                    }
                ),
                200,
            )
        except Exception as e:
            print(f"Error processing received message: {e}", "\n")
            return jsonify({"error": str(e), "status": 500}), 500

    def validate(self, *args, **kwargs):
        return super().validate(*args, **kwargs)
