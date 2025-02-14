from datetime import datetime
import pytz
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class BeinSportsDataProcessor(IDataProcessor):
    """
    A class to process Bein Sports data and filter events based on a specific date.

    This class takes raw data, extracts relevant event details such as title, 
    description, and date/time, adjusts the time zone, and returns a list of 
    processed events for a given date.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The source timezone of the events.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):
        """
        Processes raw data to extract event details and filter by the target date.

        Args:
            rawData (dict): The raw data containing event information.
            defaultDescription (str): A default description to use if no category is provided.
            targetDate (str): The date to filter events by, in the format 'YYYY-MM-DD'.

        Returns:
            list: A list of processed events for the target date, each containing:
                - 'date': The event date (string in 'YYYY-MM-DD' format).
                - 'hour': The event start time (string in 'HH:MM' format).
                - 'title': The event title (string).
                - 'content': The event description (string).
        """
        processedEvents = []

        # Iterate over each event in the raw data
        for event in rawData['rows']:
            eventContent = defaultDescription

            # Parse the event start date and time
            rawEventStartDate = event.get("startDate")
            eventStartDatetime = datetime.strptime(rawEventStartDate, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Localize the event datetime to the source timezone
            localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)

            # Convert the localized datetime to the target timezone
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            # Get the event date and time in the desired format
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            # Extract event title and description
            eventTitle = event.get("title").strip()
            eventCategory = event.get("category", "").strip()

            # If a category is available, update the content
            if eventCategory:
                eventContent = eventCategory

            # Append the processed event to the list
            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": eventTitle,
                "content": eventContent,
            })

        return processedEvents