from application.interfaces.service_interface import ServiceInterface
from infrastructure.interfaces.whatsapp_client_interface import WhatsappClientInterface


class SendMessageService(ServiceInterface):
    def __init__(
        self,
        whatsapp_client: WhatsappClientInterface,
    ) -> None:
        """
        Initialize the SendMessageService with a WhatsApp client.
        """
        self.whatsapp_client = whatsapp_client

    def execute(
        self,
        phone_number: str,
        format_message: dict,
    ) -> None:
        try:
            print(f"🔔 Enviando mensaje a {phone_number}...", "\n")

            self.whatsapp_client.send_message(format_message)

            print(f"✅ Mensaje enviado a {phone_number} con éxito.", "\n")
            return {
                "message": f"Mensaje enviado a {phone_number} con éxito.",
                "status": 200,
            }
        except Exception as e:
            print(f"❌ Error al enviar mensaje a {phone_number}: {e}", "\n")
            raise e

    def validate(self, *args, **kwargs) -> bool:
        """
        Validate the input for the service.
        """
        return True
