import pytz
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class VeneVisionDataProcessor(IDataProcessor):
    """
    A class to process Venevisión event data and filter events based on a specific date.

    This class extracts relevant event details such as title, description, and 
    date/time from raw HTML data, adjusts the time zone, and returns a list of 
    processed events for a given date.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source and target timezones.

        Args:
            timezone (str): The source timezone of the events.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: str, defaultDescription: str, targetDate: str):
        """
        Processes the raw event data, extracts relevant information, adjusts timezones,
        and returns a list of events filtered by the target date.

        Args:
            rawData (str): Raw HTML data containing event information.
            defaultDescription (str): Default description to use if no specific description is found.
            targetDate (str): The target date to filter events (format: YYYY-MM-DD).

        Returns:
            list: A list of processed event data for the target date. Each dictionary contains:
                - "date" (str): The formatted event date (YYYY-MM-DD).
                - "hour" (str): The event time in 24-hour format (HH:MM).
                - "title" (str): The event title.
                - "content" (str): The event description or default description.
        """
        processedEvents = []
        soup = BeautifulSoup(rawData, 'html.parser')

        # Extract the necessary data
        scheduleItems = soup.find_all('div', class_='item')

        for item in scheduleItems:
            # Extract the event title
            titleTag = item.find('h3', class_='ml0')
            if not titleTag:
                continue
            title = titleTag.text.strip()

            # Extract the subtitle containing date and time
            subtitleTag = item.find('p', class_='subtitle fs13 ptb3')
            subtitleText = subtitleTag.text.strip()
            rawDate, rawHour = subtitleText.split(' de ')

            # Convert date to format YYYY-MM-DD
            dateObject = datetime.strptime(rawDate, '%d-%m-%Y')
            formattedDate = dateObject.strftime('%Y-%m-%d')

            # Convert time to 24-hour format
            hourParts = rawHour.split(' a ')
            formattedTime = datetime.strptime(hourParts[0].strip(), '%I:%M %p').strftime('%H:%M')

            # Convert timezones
            startTimeObj = datetime.strptime(f"{formattedDate} {formattedTime}", "%Y-%m-%d %H:%M")
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            # Extract event description
            nextParagraph = subtitleTag.find_next('p')
            content = nextParagraph.text.strip() if nextParagraph else defaultDescription

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": content,
            })

        # Sort events chronologically by date and time
        sortedEvents = sorted(
            processedEvents,
            key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), datetime.strptime(x["hour"], "%H:%M"))
        )

        return sortedEvents
