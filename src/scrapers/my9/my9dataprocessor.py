import pytz
import re
from datetime import datetime, timedelta
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class My9DataProcessor(IDataProcessor):
    """
    A data processor for extracting and formatting TV schedule events.

    This class processes raw TV schedule data by extracting relevant details, 
    converting timestamps between time zones, and filtering events by a specified date.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source and target time zones.

        Args:
            timezone (str): The source time zone of the event data.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str):
        """
        Extracts, processes, and filters event data for a given date.

        This method parses raw schedule data, extracts event details such as title, 
        episode, and description, adjusts time zones, and returns a structured list 
        of events occurring on the specified target date.

        Args:
            rawData (dict): The raw schedule data, expected under 'Json' -> 'Channels' -> 'Days' -> 'Shows'.
            defaultDescription (str): The fallback description used if no metadata is available.
            targetDate (str): The date to filter events by, formatted as 'YYYY-MM-DD'.

        Returns:
            list[dict]: A list of processed events, each containing:
                - 'date' (str): The event date in 'YYYY-MM-DD' format.
                - 'hour' (str): The event start time in 'HH:MM' format.
                - 'title' (str): The main title of the event.
                - 'content' (str): A formatted string combining episode title and description, if available.
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
