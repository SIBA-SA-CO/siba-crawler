import pytz
import re
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class NpoDataProcessor(IDataProcessor):
    """
    A class to process NPO program data and filter events based on a specific date.

    This class extracts relevant details from raw schedule data, including title, 
    description, and start time. It converts timestamps to a specified target 
    timezone and returns a list of processed events sorted chronologically.
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
        Processes raw schedule data, extracts relevant event details, 
        converts timestamps to the target timezone, and sorts events chronologically.

        Args:
            rawData (list): A list of dictionaries containing event information.
            defaultDescription (str): Default description used if no synopsis is provided.
            targetDate (str): The target date for filtering events, formatted as 'YYYY-MM-DD'.

        Returns:
            list: A list of processed event data, each containing:
                - 'date' (str): Event date ('YYYY-MM-DD').
                - 'hour' (str): Event start time ('HH:MM').
                - 'title' (str): Program title.
                - 'content' (str): Program synopsis or default description.
        """
        processedEvents = []
        
        for program in rawData:
            programStartTimestamp = program.get("programStart")
            programTitle = program.get("mainTitle", "")
            programSynopsis = program.get("synopsis", "") or defaultDescription
            
            if not programTitle:
                continue 
            
            if programStartTimestamp:
                programStartTimestamp = programStartTimestamp // 1000 if programStartTimestamp > 10**10 else programStartTimestamp
                startTimeObj = datetime.fromtimestamp(programStartTimestamp, tz=timezone.utc).replace(tzinfo=None)
                localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
                eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
                eventTime = targetEventDatetime.strftime("%H:%M").strip()
                processedEvents.append({
                    "date": eventDate,
                    "hour": eventTime,
                    "title": programTitle,
                    "content": programSynopsis,
                })

        sortedEvents = sorted(
            processedEvents,
            key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), datetime.strptime(x["hour"], "%H:%M"))
        )

        return sortedEvents
