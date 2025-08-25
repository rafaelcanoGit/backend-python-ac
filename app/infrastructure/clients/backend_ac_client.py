from infrastructure.interfaces.backend_ac_client_interface import (
    BackendACClientInterface,
)
import requests
import json


class BackendACClient(BackendACClientInterface):

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    # 1.
    def get_contact_by_number(self, number):
        try:
            url = f"{self.api_url}/whatsapp/contacts/{number}"
            headers = {
                "Content-Type": "application/json",
            }
            print(f"🔍 Fetching contact by number: {number}", "\n")
            response = requests.get(
                url,
                headers=headers,
            )
            print(f"Response get_contact_by_number {response}", "\n")
            return response.json() if response.status_code == 200 else None
        except Exception as exception:
            print(f"❌ Error fetching contact by number: {exception}", "\n")
            raise exception

    # 2.
    def save_contact(self, phone_number):
        try:
            url = f"{self.api_url}/whatsapp/save/contact"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "phone_number": phone_number,
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            return response.json() if response.status_code == 201 else None
        except Exception as exception:
            print(f"❌ Error saving contact: {exception}", "\n")
            raise exception

    # 3.
    def delete_contact(self, contact_id):
        try:
            url = f"{self.api_url}/whatsapp/delete/contact/{contact_id}"
            headers = {
                "Content-Type": "application/json",
            }
            response = requests.delete(
                url,
                headers=headers,
            )
            return response.status_code == 204
        except Exception as exception:
            print(f"❌ Error deleting contact: {exception}", "\n")
            raise exception

    # 5.
    def update_contact_by_id(
        self, contact_id: int, column_to_update: str, new_value: str
    ) -> None:
        try:
            url = f"{self.api_url}/whatsapp/update/contact/{contact_id}"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                column_to_update: new_value,
            }
            response = requests.put(url, headers=headers, data=json.dumps(data))
            return response.status_code == 200
        except Exception as exception:
            print(f"❌ Error updating contact by ID: {exception}", "\n")
            raise exception

    # 6.
    def save_message(
        self,
        user_id: dict,
        type_sender: str,
        message: dict,
    ) -> None:
        try:
            url = f"{self.api_url}/whatsapp/save/message"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "contact_id": user_id,
                "type_sender": type_sender,
                "message": message,
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            return response.status_code == 201

        except Exception as exception:
            print(f"❌ Error saving message: {exception}", "\n")
            raise exception
