import pytz
import defusedxml.ElementTree as ET
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class WarnerDataProcessor(IDataProcessor):
    """
    Data processor for parsing and transforming raw XML data from Warner's schedule feed 
    into a structured list of program events.

    Attributes:
        sourceTimezone (pytz.timezone): Timezone of the source data.
        targetTimezone (pytz.timezone): Target timezone for the processed events, set to 'America/Bogota'.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with source and target timezones.

        Args:
            timezone (str): Timezone string representing the source data timezone.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):
        """
        Processes the raw XML data, extracts program events, and converts them into 
        a list of dictionaries with date, time, title, and description.

        Args:
            rawData (str): Raw XML string containing the schedule data.
            defaultDescription (str): Fallback description if the event has no description.
            targetDate (str): Target date (unused in current implementation, but part of interface).

        Returns:
            list[dict]: A list of processed events, where each event contains:
                - date (str): Event date in 'YYYY-MM-DD' format.
                - hour (str): Event time in 'HH:MM' format.
                - title (str): Combined program and episode title.
                - content (str): Event description.
        """
        processedEvents = []
        
        root = ET.fromstring(rawData)
        events = root[1].findall('Schedule')

        for event in events:
            title = ""
            content = defaultDescription

            # Parse and convert event datetime
            gmt = event.find('gmt').text
            parseDate = datetime.strptime(gmt, "%a %b %d %H:%M:%S GMT %Y")
            localizedEventDatetime = self.sourceTimezone.localize(parseDate)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            # Extract show and episode details
            show = event.find('show')
            episode = show.find('episode')
            programTitle = show.find('programTitle').text
            episodeTitle = episode.find('episodeTitle').text
            description = episode.find('description').text

            # Build title
            if programTitle and episodeTitle:
                title = f"{programTitle} - {episodeTitle}"
            else:
                title = programTitle

            # Use episode description if available
            if description:
                content = description

            # Add processed event to list
            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": content,
            })

        return processedEvents
