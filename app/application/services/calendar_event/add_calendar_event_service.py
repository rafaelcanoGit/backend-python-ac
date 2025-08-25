from typing import Any, Dict
from application.interfaces.service_interface import ServiceInterface
from infrastructure.interfaces.google_calendar_client_interface import (
    GoogleCalendarClientInterface,
)
from datetime import datetime, timedelta


class AddCalendarEventService(ServiceInterface):

    def __init__(self, google_calendar_client: GoogleCalendarClientInterface) -> None:
        """
        Initialize the AddCalendarEventService with a Google Calendar client.
        """
        self.google_calendar_client = google_calendar_client

    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the service logic to add a calendar event.

        :param args: Positional arguments for the service.
        :param kwargs: Keyword arguments for the service.
        :return: A dictionary containing the result of the operation.
        """
        try:
            print("🔔 Adding calendar event...", "\n")

            summary = kwargs.get("summary", "Default Event Summary")
            description = kwargs.get("description", "Default Event Description")
            start = kwargs.get("start", datetime.utcnow().isoformat() + "Z")
            end = kwargs.get(
                "end",
                (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
            )
            attendees = kwargs.get("attendees", [])

            event = self.google_calendar_client.add_event(
                "andrescanchica.consultorio@gmail.com",
                summary,
                description,
                start,
                end,
                attendees,
            )
            print("✅ Calendar event added successfully. Event details:", event, "\n")

            return {"event": event}
        except Exception as e:
            print(f"❌ Error adding calendar event: {e}", "\n")
            raise e

    def validate(self, *args, **kwargs):
        """
        Validate the service parameters.
        """
        return super().validate(*args, **kwargs)
