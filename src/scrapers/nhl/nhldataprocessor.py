import pytz
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class NhlDataProcessor(IDataProcessor):
    """
    A class to process NHL event data and filter events based on a specific date.

    This class processes raw schedule data, extracts relevant details such as 
    title, description, and start time, adjusts time zones, and returns a sorted 
    list of processed events.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source and target timezones.

        Args:
            timezone (str): The source timezone of the event data.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str):
        """
        Processes raw schedule data, extracts event details, converts timestamps, 
        and returns a sorted list of events.

        Args:
            rawData (dict): A dictionary containing schedule data under the key 'broadcasts'.
            defaultDescription (str): A default description to use if no specific event description is found.
            targetDate (str): The target date to filter events (format: 'YYYY-MM-DD').

        Returns:
            list: A sorted list of processed events occurring on the target date, 
                  each containing:
                  - 'date' (str): The event date ('YYYY-MM-DD').
                  - 'hour' (str): The event start time ('HH:MM').
                  - 'title' (str): The event title.
                  - 'content' (str): A formatted description of the event.
        """
        processedEvents = []
        
        for broadcast in rawData['broadcasts']:
            content = defaultDescription
            rawStartTime = broadcast.get("startTime")
            
            startTimeObj = datetime.fromisoformat(rawStartTime)
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            title = broadcast.get("title") or title
            description = broadcast.get("description") or description

            if description:
                content = description

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": content,
            })

        sortedEvents = sorted(
            processedEvents,
            key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), datetime.strptime(x["hour"], "%H:%M"))
        )

        return sortedEvents
