import pytz
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class BvnTvDataProcessor(IDataProcessor):
    """
    A data processor class that extracts, formats, and filters event details from raw data.

    This class processes raw event data, converts event timestamps from the source timezone
    to the target timezone ("America/Bogota"), and filters events based on a specific target date.
    Each processed event includes details such as date, time, title, and a formatted description.

    Attributes:
        sourceTimezone (pytz.timezone): The timezone of the source event data.
        targetTimezone (pytz.timezone): The target timezone for event time conversion.
    """

    def __init__(self, timezone: str):
        """
        Initializes the BvnTvDataProcessor with the source timezone.

        Args:
            timezone (str): The timezone of the source event data (e.g., "UTC").
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: list, defaultDescription: str, targetDate: str) -> list:
        """
        Processes raw event data to extract, format, and filter events for the target date.

        Args:
            rawData (list): A list of dictionaries containing event information.
            defaultDescription (str): A default description to use if no event metadata is available.
            targetDate (str): The target date to filter events by, formatted as 'YYYY-MM-DD'.

        Returns:
            list: A list of dictionaries, each representing a processed event with the following keys:
                - 'date' (str): The event date in 'YYYY-MM-DD' format.
                - 'hour' (str): The event start time in 'HH:MM' format.
                - 'title' (str): The title of the event.
                - 'content' (str): A formatted description of the event, using the synopsis if available,
                  or falling back to the default description.
        """
        processedEvents = []

        # Iterate over each event in the raw data
        for event in rawData:
            eventContent = defaultDescription  # Default content if no metadata is found

            # Parse the event start date and time
            rawEventStartDate = event.get("start")
            eventStartDatetime = datetime.strptime(rawEventStartDate, "%Y-%m-%d %H:%M:%S")

            # Localize the event datetime to the source timezone
            localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)

            # Convert the event time to the target timezone
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            # Format the event date and time
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            # Extract event details
            eventTitle = event.get("title", "").strip()
            synopsis = event.get("content", "")

            # Skip events without a title
            if not eventTitle:
                continue

            # Use synopsis as content if available
            if synopsis:
                eventContent = synopsis

            # Filter events by the target date and add to the processed list
            if eventDate == targetDate:
                processedEvents.append({
                    "date": eventDate,
                    "hour": eventTime,
                    "title": eventTitle,
                    "content": eventContent,
                })

        return processedEvents