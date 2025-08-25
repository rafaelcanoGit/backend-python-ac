from infrastructure.interfaces.whatsapp_client_interface import WhatsappClientInterface
import requests
import json


class WhatsappClient(WhatsappClientInterface):

    def __init__(self, whatsapp_api_url: str, token: str) -> None:
        """Initialize the WhatsApp client with the API URL and token."""
        self.whatsapp_api_url = whatsapp_api_url
        self.token = token

    def send_message(self, format_message: dict) -> None:
        """
        Send a message to a WhatsApp number.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        try:
            response = requests.post(
                self.whatsapp_api_url, data=json.dumps(format_message), headers=headers
            )

            print(f"========= Response from WhatsApp API: =========== \n")
            print(f"Response message: {response.text}", "\n")
            print(f"Response status code: {response.status_code}", "\n")

            # return response.status_code == 200

        except Exception as exception:
            print(f"❌ Error sending message: {exception}", "\n")
            raise exception
