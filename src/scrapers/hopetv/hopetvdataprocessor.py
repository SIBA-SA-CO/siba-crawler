import pytz
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class HopeTvDataProcessor(IDataProcessor):
    """
    Processes Hope TV schedule data, extracts relevant details, adjusts timezones,
    and returns a list of formatted events.
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
        Extracts and processes event data, adjusting timezones and formatting output.

        Args:
            rawData (list): List of raw event data.
            defaultDescription (str): Default description if none is provided.
            targetDate (str): Target date to filter events (format: YYYY-MM-DD).

        Returns:
            list: A list of processed events, each containing date, time, title, and content.
        """
        processedEvents = []

        for event in rawData:
            eventContent = defaultDescription
            startTimeUtc = event.get("startsAt", "")
            showTitle = event.get("showTitle", "").strip()
            episodeTitle = event.get("episodeTitle", "")
            eventDescription = event.get("description", "")

            if not showTitle:
                showTitle = event.get("episode", {}).get("show", {}).get("title", "")
                episodeTitle = event.get("episode", {}).get("title", "")

            if episodeTitle and eventDescription:
                eventContent = f"{episodeTitle} - {eventDescription}"
            elif episodeTitle:
                eventContent = episodeTitle
            elif eventDescription:
                eventContent = eventDescription

            startTimeObj = datetime.fromisoformat(startTimeUtc.replace("Z", "+00:00")).replace(tzinfo=None)
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": showTitle,
                "content": eventContent,
            })

        return processedEvents
