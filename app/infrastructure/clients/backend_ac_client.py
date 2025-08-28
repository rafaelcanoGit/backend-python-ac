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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.159 Safari/537.36",
                "Connection": "keep-alive",
            }
            print(f"🔍 Fetching contact by number: {number}", "\n")
            print(f"URL: {url}", "\n\n")
            response = requests.get(
                url,
                headers=headers,
            )
            print(f"Response statrs get_contact_by_number {response.status_code}", "\n")
            print(f"Response body get_contact_by_number {response.text}", "\n\n")
            print("--------------------------------------------------", "\n")
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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.159 Safari/537.36",
                "Connection": "keep-alive",
            }
            data = {
                "phone_number": phone_number,
            }
            print(f"🔍 Saving contact: {phone_number}", "\n")
            print("Data:", data, "\n")
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(f"Response status save_contact {response.status_code}", "\n")
            print(f"Response body save_contact {response.text}", "\n\n")

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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.159 Safari/537.36",
                "Connection": "keep-alive",
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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.159 Safari/537.36",
                "Connection": "keep-alive",
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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.159 Safari/537.36",
                "Connection": "keep-alive",
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
