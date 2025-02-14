import pytz
import re
import json
from datetime import datetime, timezone
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class GameShowNetworkDataProcessor(IDataProcessor):
    """
    A class to process Game Show Network event data and filter events based on a specific date.

    This class takes raw HTML data, extracts relevant event details such as title, 
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

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        """
        Processes the raw event data, extracts relevant information, adjusts timezones,
        and returns a list of events filtered by the target date.

        Args:
            rawData (str): Raw HTML data containing event information.
            defaultDescription (str): Default description to use if no specific description is found.
            targetDate (str): The target date to filter events (format: 'YYYY-MM-DD').

        Returns:
            list: A list of dictionaries, each representing a processed event with the following keys:
                - 'date' (str): The event date in 'YYYY-MM-DD' format.
                - 'hour' (str): The event start time in 'HH:MM' format.
                - 'title' (str): The title of the event.
                - 'content' (str): A formatted description of the event, combining host and description
                  if available, or falling back to the default description.
        """
        processedEvents = []

        # Parse the HTML content to extract the schedule data
        pattern = r'<script[^>]*>\s*siteSettings\.schedule\s*=\s*(\[.*?\]);'
        match = re.search(pattern, rawData, re.DOTALL)

        if match:
            schedule = match.group(1)
            data = json.loads(schedule)

            # Iterate over each event in the schedule data
            for item in data:
                eventContent = defaultDescription  # Default content if no metadata is found

                # Extract event details
                programStart = item.get('startTime')
                title = item.get('title')
                host = item.get('host', "")
                description = item.get('description', "")

                # Parse and convert the event start time
                eventStartDatetime = datetime.fromtimestamp(programStart, tz=timezone.utc).replace(tzinfo=None)
                localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

                # Format the event date and time
                eventDate = targetEventDatetime.strftime("%Y-%m-%d")
                eventTime = targetEventDatetime.strftime("%H:%M")

                # Construct the event content based on available data
                if description and host:
                    eventContent = f"{host} - {description}"
                elif description:
                    eventContent = description
                elif host:
                    eventContent = host

                # Append the processed event to the list
                processedEvents.append({
                    "date": eventDate,
                    "hour": eventTime,
                    "title": title,
                    "content": eventContent,
                })

        return processedEvents