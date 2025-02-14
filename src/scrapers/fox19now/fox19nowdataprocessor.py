import pytz
import re
from datetime import datetime, timedelta
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class Fox19NowDataProcessor(IDataProcessor):


    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The source timezone of the events.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str):
        """
        Processes raw data to extract event details, convert timestamps, and filter by a specific date.

        Args:
            rawData (dict): A dictionary containing event data under the key 'tvSchedules'.
            defaultDescription (str): Default description if no event metadata is provided.
            targetDate (str): The date to filter events by, formatted as 'YYYY-MM-DD'.

        Returns:
            list: A list of processed events occurring on the target date, each with:
                - 'date' (str): The event date ('YYYY-MM-DD').
                - 'hour' (str): The event start time ('HH:MM').
                - 'title' (str): The event title.
                - 'content' (str): A formatted description of the event.
        """
        processedEvents = []

        # Iterate through each event in the provided raw data
        for show in rawData['Json']['Channels'][0]["Days"][0]["Shows"]:
            eventContent = defaultDescription  # Default content if no metadata is found

            # Extract and parse the event start date and time
            programStart = show.get("StartTime")
            
            # Parse the event start time
            eventStartDatetime = datetime.fromisoformat(programStart).replace(tzinfo=None)

            localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)

            # Convert to the target timezone
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            # Extract formatted date and time
            eventDate = targetEventDatetime.strftime("%Y-%m-%d")
            eventTime = targetEventDatetime.strftime("%H:%M")

            # Safely extract titles
            mainTitle = (
                show.get("Title", [{}])[0].get("Text")
                if show.get("Title") and len(show.get("Title")) > 0
                else "n/a"
            )

            episodeTitle = (
                show.get("EpisodeTitle", [{}])[0].get("Text")
                if show.get("EpisodeTitle") and len(show.get("EpisodeTitle")) > 0
                else "n/a"
            )

            # Safely extract descriptions
            synopsis = (
                show.get("Description", [{}])[0].get("Text")
                if show.get("Description") and len(show.get("Description")) > 0
                else "n/a"
            )

            # Skip "No Programming Available" entries
            if mainTitle == "No Programming Available":
                continue

            # Construct event content based on available data
            if synopsis != "n/a" and episodeTitle != "n/a":
                eventContent = f"{episodeTitle} - {synopsis}"
            elif synopsis != "n/a":
                eventContent = synopsis
            elif episodeTitle != "n/a":
                eventContent = episodeTitle

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": mainTitle,
                "content": eventContent,
            })

        return processedEvents
