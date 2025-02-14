import pytz
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class StartTvDataProcessor(IDataProcessor):
    """
    A data processor for extracting and formatting TV schedule events from Start TV.

    This class processes raw HTML schedule data by extracting relevant details 
    such as title, description, and time. It also converts event times to the 
    target timezone and returns a list of formatted events.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The timezone of the original schedule data.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        """
        Extracts and processes TV schedule data from HTML.

        Args:
            rawData (str): The raw HTML containing the TV schedule.
            defaultDescription (str): The default description to use if no event metadata is available.
            targetDate (str): The date for which the schedule is being processed, formatted as 'YYYY-MM-DD'.

        Returns:
            list: A sorted list of processed events, where each event contains:
                - 'date' (str): The event date ('YYYY-MM-DD').
                - 'hour' (str): The event start time ('HH:MM').
                - 'title' (str): The event title.
                - 'content' (str): A formatted description of the event.
        """
        processedEvents = []
        soup = BeautifulSoup(rawData, 'html.parser')

        # Find all schedule items on the page
        scheduleItems = soup.find_all('div', class_='sched-item clearfix')

        for item in scheduleItems:
            timeString = item.find('div', class_='sched-show-time').text.strip()
            showTime = datetime.strptime(timeString, "%I:%M%p").strftime("%H:%M")
            startTimeObj = datetime.strptime(f"{targetDate} {showTime}", "%Y-%m-%d %H:%M")

            # Convert timezone
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            title = item.find('h1', class_='hp-section-header sched-inline').text.strip()

            episodeTitle = ""
            description = ""
            content = defaultDescription
            
            descriptionElement = item.find('div', class_='sched-show-desc')

            if descriptionElement:
                episodeElement = descriptionElement.find('h2')
                episodeTitle = episodeElement.text.strip() if episodeElement else ""
                description = (
                    episodeElement.next_sibling.strip() if episodeElement and episodeElement.next_sibling else ""
                )

            if episodeTitle and description:
                content = f"{episodeTitle} - {description}"
            elif episodeTitle:
                content = episodeTitle
            elif description:
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
