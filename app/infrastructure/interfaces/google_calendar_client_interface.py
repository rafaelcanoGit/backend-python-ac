from abc import ABC, abstractmethod


class GoogleCalendarClientInterface(ABC):

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the Google Calendar API.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the Google Calendar API.
        """
        pass

    @abstractmethod
    def get_connection(self):
        """
        Get the current connection to the Google Calendar API.

        :return: The connection object.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection to the Google Calendar API is active.

        :return: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def add_event(self, calendar_email: str, summary: str, start: str, end: str):
        """
        Add an event to the Google Calendar.

        :param calendar_email: Email of the calendar where the event will be added.
        :param summary: Summary of the event.
        :param start_date_time: Start date and time of the event in ISO format.
        :param end_date_time: End date and time of the event in ISO format.
        :return: The created event object.
        """
        pass

    @abstractmethod
    def get_available_slots(self, calendar_email: str) -> dict:
        """
        Get available time slots for a given calendar within a specified date range.

        :param calendar_email: Email of the calendar to check.
        :param start_date: Start date of the range in ISO format.
        :param end_date: End date of the range in ISO format.
        :return: A dictionary containing available time slots.
        """
        pass
    
    @abstractmethod
    def schedule_pre_consultation(self, full_name, type_consultation, user_phone, start, end):
        """
        Schedule a pre-consultation event in the Google Calendar.

        :param full_name: Full name of the user.
        :param type_consultation: Type of consultation.
        :param user_phone: Phone number of the user.
        :param start: Start date and time of the event in ISO format.
        :param end: End date and time of the event in ISO format.
        :return: The created event object.
        """
        pass
