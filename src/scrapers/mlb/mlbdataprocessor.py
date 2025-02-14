import pytz
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class MlbDataProcessor(IDataProcessor):
    """
    A data processor for MLB event schedules.

    This class processes raw event data by extracting relevant details such as 
    the event title, episode name, description, and start time. It also converts 
    time zones from the source to the target timezone and formats the data into 
    a structured list.

    Attributes:
        sourceTimezone (pytz.timezone): The original timezone of the event schedule.
        targetTimezone (pytz.timezone): The target timezone for converting event times.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The timezone in which the original event schedule is provided.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):
        """
        Processes raw MLB event data by extracting event details, converting timezones, 
        and filtering events based on the target date.

        Args:
            rawData (dict): A dictionary containing event data with fields such as 
                            'startdate', 'starttime', 'umbrellatitle', 'seriestitle',
                            'episodetitle', and 'synopsis'.
            defaultDescription (str): The default description to use if no valid 
                                      episode title or synopsis is available.
            targetDate (str): The target date to filter events, formatted as 'YYYY-MM-DD'.

        Returns:
            list of dict: A list of processed events, where each event is represented as a dictionary with:
                - "date" (str): The event date in 'YYYY-MM-DD' format.
                - "hour" (str): The event time in 'HH:MM' format (24-hour).
                - "title" (str): The main title of the event.
                - "content" (str): A combined description including episode title and synopsis.
        """
        processedEvents = []

        for show in rawData['shows']:
            content = defaultDescription
            
            rawDate = show.get("startdate")
            rawTime = show.get("starttime")
            
            dateObj = datetime.strptime(rawDate, '%m/%d/%Y')
            timeObj = datetime.strptime(rawTime, "%I:%M %p")
            
            # Combine date and time into a single datetime object
            startTimeObj = datetime.combine(dateObj, timeObj.time())
            
            # Check if the datetime object is naive (doesn't have timezone info)
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            
            # Convert the localized datetime to the target timezone
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            
            # Get the event date and time in the desired format
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()
            
            mainTitle = show.get("umbrellatitle") or show.get("seriestitle")
            
            if not mainTitle:
                continue
            
            episodeTitle = show.get("episodetitle")
            synopsis = show.get("synopsis")
            
            if episodeTitle and synopsis:
                content = f"{episodeTitle} - {synopsis}"
            elif episodeTitle:
                content = episodeTitle
            elif synopsis:
                content = synopsis
            
            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": mainTitle,
                "content": content,
            })


        return processedEvents
