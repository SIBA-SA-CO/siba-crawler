import re
import pytz
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class EwtnDataProcessor(IDataProcessor):
    """
    Processes EWTN event data by extracting, formatting, and filtering events based on a target date.
    
    This class parses raw HTML data, extracts relevant details such as title, description, and schedule,
    adjusts time zones, and returns a list of structured event data for a specified date.
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
        Parses and processes raw event data, extracts details, adjusts timezones,
        and returns a list of events occurring on the specified target date.

        Args:
            rawData (str): Raw HTML data containing event details.
            defaultDescription (str): Default description to use when no specific description is available.
            targetDate (str): Target date to filter events (format: YYYY-MM-DD).

        Returns:
            list[dict]: A list of processed event data, each containing the date, time, title, and content.
        """
        processedEvents = []

        # Parse HTML content
        soup = BeautifulSoup(rawData, 'html.parser')
        entries = soup.find_all('div', class_='schedule__entry')
        if not entries:
            return processedEvents

        # Extract relevant data from each event
        for event in entries:
            eventContent = defaultDescription

            titleContainer = event.find('div', class_='schedule__title')
            if not titleContainer:
                continue
            title = re.sub(r'\s+', ' ', titleContainer.text.strip().replace("\n", " "))

            subtitleContainer = event.find('h3', class_='schedule__sub-title')
            subtitle = re.sub(r'\s+', ' ', subtitleContainer.text.strip().replace("\n", " ")) if subtitleContainer else 'n/a'

            descriptionContainer = event.find('p', class_='schedule__description')
            description = re.sub(r'\s+', ' ', descriptionContainer.text.strip().replace("\n", " ")) if descriptionContainer else 'n/a'

            # Determine final event content
            if subtitle and description:
                eventContent = f"{subtitle} - {description}"
            elif subtitle:
                eventContent = subtitle
            elif description:
                eventContent = description

            # Extract event time and convert to target timezone
            timeContainer = event.find('div', class_='schedule__time')
            startTime = timeContainer['data-datetime'] if timeContainer and 'data-datetime' in timeContainer.attrs else None
            if not startTime:
                continue
            startTimeObj = datetime.fromisoformat(startTime.replace("Z", "+00:00")).replace(tzinfo=None)
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            # Format final date and time
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": eventContent,
            })

        return processedEvents