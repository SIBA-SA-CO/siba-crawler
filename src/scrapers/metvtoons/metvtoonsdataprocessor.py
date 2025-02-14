import pytz
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class MeTvToonsDataProcessor(IDataProcessor):
    """
    A data processor for MeTV Toons schedule information.

    This class processes raw schedule data, extracting relevant details such as 
    show titles, episode names, descriptions, and broadcast times. It converts 
    time zones from the source timezone to the target timezone and formats 
    the data into a structured list.

    Attributes:
        sourceTimezone (pytz.timezone): The timezone of the original schedule data.
        targetTimezone (pytz.timezone): The target timezone for converting event times.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The timezone from which the raw schedule data originates.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):
        """
        Processes raw schedule data by converting times, extracting relevant details, 
        and formatting it into a structured list sorted by date and time.

        Args:
            rawData (list of tuples): A list of extracted schedule data where each 
                entry contains (date, show_time, show_title, episode_title, description).
            defaultDescription (str): The default description to use if no valid 
                description or episode title is available.
            targetDate (str): The date for which the events should be filtered, 
                formatted as 'YYYY-MM-DD'.

        Returns:
            list of dict: A list of processed events, each represented as a dictionary with:
                - "date" (str): The event date in 'YYYY-MM-DD' format.
                - "hour" (str): The event time in 'HH:MM' format (24-hour).
                - "title" (str): The show title.
                - "content" (str): A combined description including episode title and details.
        """
        processedEvents = []
        
        for date, showTime, showTitle, episodeTitle, description in rawData:
            startTimeObj = datetime.strptime(f"{date} {showTime}", "%Y-%m-%d %H:%M")
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            content = (
                f"{episodeTitle} - {description}" if description != "n/a" and episodeTitle != "n/a"
                else description if description != "n/a"
                else episodeTitle if episodeTitle != "n/a"
                else defaultDescription
            )

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": showTitle,
                "content": content,
            })

        sortedEvents = sorted(
            processedEvents,
            key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), datetime.strptime(x["hour"], "%H:%M"))
        )

        return sortedEvents
