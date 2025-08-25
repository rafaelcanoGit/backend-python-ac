from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone, time
import json
import os
from pathlib import Path
import uuid
from infrastructure.interfaces.google_calendar_client_interface import (
    GoogleCalendarClientInterface,
)
from domain.calendar_event.helpers.calendar_helper import (
    review_available_slot_on_consult_days,
    group_availables_slots_by_days,
)
from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)


class GoogleCalendarClient(GoogleCalendarClientInterface):

    def __init__(
        self, whatsapp_repository: WhatsappRepositoryInterface, webhook_url
    ) -> None:
        self.service = None
        self.creds = None
        self.SERVICE_ACCOUNT_FILE = None
        self.SCOPES = ["https://www.googleapis.com/auth/calendar"]
        self.utc_5 = "-05:00"
        self.whatsapp_repository = whatsapp_repository
        self.connect()
        # self.register_webhook(webhook_url)

    def __del__(self):
        """
        Destructor to close the connection when the client is destroyed.
        """
        self.disconnect()

    def connect(self):
        """
        Connect to the Google Calendar API.
        """
        try:
            self.SERVICE_ACCOUNT_FILE = os.path.join(
                os.getcwd(),
                "credenciales-google-calendar",
                "calendar-ac-consultorio-58c0244c52dd.json",
            )

            if self.SERVICE_ACCOUNT_FILE:
                print(
                    f"File SERVICE_ACCOUNT_FILE found ✅: {self.SERVICE_ACCOUNT_FILE}",
                    "\n",
                )
            else:
                print("File SERVICE_ACCOUNT_FILE not found ❌.", "\n")

            self.creds = Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
            )
            self.service = build("calendar", "v3", credentials=self.creds)

            print("Google Calendar API connection established. ✅")
            return True
        except Exception as e:
            print(f"Error connecting to Google Calendar API: {e}")
            return False

    def register_webhook(self, webhook_url):
        """
        Register a webhook to receive notifications from Google Calendar.
        :param webhook_url: The public URL to receive notifications.
        """
        channel_id = f"calendar_events_drandrescanchica-{uuid.uuid4()}"
        channel = {
            "id": channel_id,  # UUID único
            "type": "web_hook",
            "address": webhook_url,  # URL pública
            # "token": "TU_TOKEN_SECRETO",  # Opcional para seguridad
            "params": {"ttl": "604800"},  # 7 días (máximo permitido)
        }
        print("Registering webhook with Google Calendar API:", channel)
        self.service.events().watch(
            calendarId="andrescanchica.consultorio@gmail.com", body=channel
        ).execute()

    def get_connection(self):
        """
        Get the connection to the Google Calendar API.
        """
        try:
            if not self.service:
                self.connect()

            print("Google Calendar API connection retrieved successfully. ✅")
            return self.service
        except Exception as e:
            print(f"Error getting Google Calendar connection: {e}")
            return None

    def disconnect(self):
        """
        Disconnect from the Google Calendar API.
        """
        try:
            self.service = None
            self.creds = None
            print("Disconnected from Google Calendar API.")
        except Exception as e:
            print(f"Error disconnecting from Google Calendar API: {e}")

    def is_connected(self) -> bool:
        """
        Check if the connection to the Google Calendar API is active.

        :return: True if connected, False otherwise.
        """
        return self.service is not None and self.creds is not None

    def add_event(self, calendar_email, summary, description, start, end, attendees=[]):
        """
        Add an event to the Google Calendar.

        :param calendar_email: Email of the calendar where the event will be added.
        :param summary: Summary of the event.
        :param start: Start date and time of the event in ISO format.
        :param end: End date and time of the event in ISO format.
        :return: The created event object.
        """
        try:
            service = self.get_connection()
            if not service:
                raise Exception("Google Calendar service is not connected.")

            event = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start, "timeZone": "UTC-5"},
                "end": {"dateTime": end, "timeZone": "UTC-5"},
                "attendees": attendees,
                "time_zone": "America/Bogota",
            }

            print(f"Adding event to Google Calendar: {event}")

            created_event = (
                service.events().insert(calendarId=calendar_email, body=event).execute()
            )

            print(f"Event created ✅: {created_event.get('htmlLink')}")
            return created_event
        except Exception as e:
            print(f"Error adding event to Google Calendar: {e}")
            raise e

    def get_available_slots(self, calendar_email):
        try:
            service = self.get_connection()
            if not service:
                raise Exception("Google Calendar service is not connected.")

            current_day = datetime.utcnow()

            six_months_from_now = current_day + timedelta(days=179)

            days_of_week = ["TUESDAY", "THURSDAY"]

            busy_periods = []
            consult_days = []
            # Iterar desde la fecha actual hasta 45 días después
            while current_day <= six_months_from_now:

                # Verificar si el día actual es uno de los días de consulta (Tuesday or Thursday)
                if current_day.strftime("%A").upper() in days_of_week:

                    # Calcular inicio y fin del día
                    start_of_day = datetime(
                        current_day.year, current_day.month, current_day.day, 9, 00, 00
                    )
                    end_of_day = datetime(
                        current_day.year, current_day.month, current_day.day, 18, 00, 00
                    )

                    # Agregar el día de consulta
                    consult_days.append(
                        {
                            "start": start_of_day.isoformat() + self.utc_5,
                            "end": end_of_day.isoformat() + self.utc_5,
                        }
                    )

                    # Crear objeto de solicitud para freeBusy
                    request_body = {
                        "timeMin": start_of_day.isoformat() + self.utc_5,
                        "timeMax": end_of_day.isoformat() + self.utc_5,
                        "timeZone": "UTC-5",
                        "items": [{"id": calendar_email}],
                    }

                    # Realizar solicitud freeBusy para obtener horarios ocupados
                    response = service.freebusy().query(body=request_body).execute()
                    busy_times = response["calendars"][calendar_email]["busy"]

                    for busy_time in busy_times:
                        busy_start = datetime.fromisoformat(busy_time["start"])
                        busy_end = datetime.fromisoformat(busy_time["end"])
                        busy_periods.append((busy_start, busy_end))

                    # Agregar de 12pm a 2pm como un período ocupado.
                    utc_minus_5 = timezone(timedelta(hours=-5))
                    twelve_pm = datetime.combine(
                        start_of_day.date(), time(hour=12, tzinfo=utc_minus_5)
                    )
                    two_pm = twelve_pm + timedelta(hours=2)
                    busy_periods.append((twelve_pm, two_pm))

                # Avanzar al siguiente día
                current_day += timedelta(days=1)

            # Revisión en días de consulta por available_slots
            available_slots = review_available_slot_on_consult_days(
                busy_periods, consult_days
            )

            return group_availables_slots_by_days(available_slots)
        except Exception as e:
            print(f"Error getting available slots from Google Calendar: {e}")
            raise e

    def is_slot_available(self, start, end, calendar_email):
        """
        Verifica si un intervalo de tiempo está disponible en Google Calendar.

        :param start: Fecha y hora de inicio (formato RFC3339, ej: '2025-07-29T09:00:00-05:00').
        :param end: Fecha y hora de fin (formato RFC3339).
        :param calendar_email: Correo del calendario a consultar.
        :return: True si el espacio está libre, False si está ocupado o ocurre un error.
        """
        if not all([start, end, calendar_email]):
            raise ValueError("start, end, and calendar_email must be provided")

        try:
            service = self.get_connection()
            if not service:
                raise Exception("Google Calendar service is not connected.")

            request_body = {
                "timeMin": start + self.utc_5,
                "timeMax": end + self.utc_5,
                "timeZone": "America/Bogota",
                "items": [{"id": calendar_email}],
            }
            print(
                "🔍 Verificando disponibilidad del horario en Google Calendar...",
                request_body,
            )
            response = service.freebusy().query(body=request_body).execute()
            busy_times = response["calendars"][calendar_email]["busy"]

            print(
                "🔍 El horario {start} - {end} está disponible:", len(busy_times) == 0
            )
            return len(busy_times) == 0
        except Exception as e:
            print(f"Error checking slot availability: {e}")
            return False

    def schedule_pre_consultation(
        self, full_name, type_consultation, user_phone, start, end
    ):
        """
        Schedule a pre-consultation event in the Google Calendar.

        :param summary: Summary of the event.
        :param full_name: Full name of the user.
        :param type_consultation: Type of consultation.
        :param user_phone: User's phone number.
        """
        try:
            summary = f"Pre-agendamiento Consulta - {full_name}"
            description = f"Tipo de consulta: {type_consultation}\nTeléfono de contacto: {user_phone}\n\nConsulta pre-agendada aútomaticamente por App AC."

            print(
                f"📆 Data to save in Google Calendar: {summary}, {description}, {start}, {end}",
                "\n",
            )  # Ex: "2025-07-29T10:00:00-05:00"

            # Verificar si ya existe un evento en ese horario, antes de crear uno nuevo.
            is_slot_available = self.is_slot_available(
                start, end, "andrescanchica.consultorio@gmail.com"
            )

            if not is_slot_available:
                return {
                    "format_type": "text",
                    "response": {
                        "message": "Lo siento, pero ya existe una consulta agendada en ese horario. ¿Te gustaría elegir otro horario?",
                    },
                }

            event = self.add_event(
                "andrescanchica.consultorio@gmail.com", summary, description, start, end
            )
            eventHtmlLink = event.get("htmlLink")

            if not eventHtmlLink:
                raise Exception("Event link not found in the created event. ❌")

            print(
                f"Pre-consultation scheduled successfully ✅. Event link: {eventHtmlLink}"
            )
            user = self.whatsapp_repository.get_contact_by_number(user_phone)

            if not user:
                raise Exception("User not found in the database. ❌")

            self.whatsapp_repository.update_contact_by_id(
                user["id"], "status", "PRE_SCHEDULED"
            )

            self.whatsapp_repository.update_contact_by_id(
                user["id"], "event_link", eventHtmlLink
            )

            fecha = datetime.fromisoformat(start.replace("Z", "+00:00"))

            return {
                "format_type": "template_confirm_payment",
                "response": {
                    "message": f"Tu consulta ha sido pre-agendada con éxito para el {fecha.strftime('%d %B de %Y a las %I:%M %p')}.\n\n ¿Te parace si continuamos con el pago, para confirmar tu cita?",
                    "fecha": fecha.strftime("%d %B de %Y"),
                    "hora": fecha.strftime("%I:%M %p"),
                },
            }
        except Exception as e:
            print(f"Error scheduling pre-consultation: {e}")
            raise e
