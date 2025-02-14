import pytz
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class TbnDataProcessor(IDataProcessor):
    """
    A class to process TV schedule data from TBN.

    This class extracts program details from raw HTML, including title, 
    description, and broadcast time. It also converts time zones and returns 
    a structured list of scheduled programs.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The timezone of the source data.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):
        """
        Processes raw HTML data to extract and format the TV schedule.

        Args:
            rawData (str): The raw HTML content containing the schedule data.
            defaultDescription (str): The default description to use if no description is available.
            targetDate (str): The target date for which events are being processed (format: 'YYYY-MM-DD').

        Returns:
            list[dict]: A sorted list of processed TV schedule events, each containing:
                - "date" (str): The broadcast date in 'YYYY-MM-DD' format.
                - "hour" (str): The broadcast time in 'HH:MM' format.
                - "title" (str): The program title.
                - "content" (str): The program description.
        """
        processedEvents = []
        soup = BeautifulSoup(rawData, 'html.parser')

        # Find all schedule items on the page
        episodeRows = soup.find_all('tr', class_='episode-row')

        for row in episodeRows:
            content = defaultDescription

            dateStr = row.get('data-timestamp')
            startTimeObj = datetime.fromisoformat(str(dateStr))
            
            # Convert timezone
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()
            

            # Program title
            titleElement = row.find('td', class_='title-column')
            title = titleElement.text.strip()

            # Description
            descriptionElement = row.get('data-synopsis')
            if descriptionElement:
                descriptionElement = descriptionElement.strip()

                if descriptionElement.startswith('<') and '>' in descriptionElement:
                    soup = BeautifulSoup(descriptionElement, 'html.parser')
                    content = soup.get_text(strip=True)
                else:
                    content = descriptionElement 

              
                content = re.sub(r'\s+', ' ', content).strip()

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
