import pytz
from bs4 import BeautifulSoup
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class MeTvDataProcessor(IDataProcessor):
    """
    A class to process and extract event details from raw HTML data.

    This class extracts event details such as title, description, and time from raw HTML,
    converts timestamps between timezones, and filters events based on a specific target date.
    """

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The source timezone of the events.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        """
        Extracts event details, converts timestamps, and filters events by the target date.

        Args:
            rawData (str): Raw HTML containing schedule data.
            defaultDescription (str): Default description to use if no event metadata is found.
            targetDate (str): The target date to filter events by, formatted as 'YYYY-MM-DD'.

        Returns:
            list: A list of dictionaries, each representing a processed event with the following keys:
                - 'date' (str): The event date in 'YYYY-MM-DD' format.
                - 'hour' (str): The event start time in 'HH:MM' format.
                - 'title' (str): The title of the event.
                - 'content' (str): A formatted description of the event, combining episode title and
                  description if available, or falling back to the default description.
        """
        processedEvents = []
        soup = BeautifulSoup(rawData, 'html.parser')
        scheduleItems = soup.find_all('div', class_='schedule-item-wrap')

        # Iterate over each schedule item in the HTML
        for item in scheduleItems:
            # Extract and clean the event time
            timeRaw = item.find('span', class_='schedule-on-now').get_text(strip=True)
            timeCleaned = timeRaw.split('Now:', 1)[-1].strip()
            originalTime = datetime.strptime(timeCleaned, "%I:%M%p")
            formattedTime = originalTime.strftime("%H:%M")

            # Parse and convert the event time to the target timezone
            startTimeObj = datetime.strptime(f"{targetDate} {formattedTime}", "%Y-%m-%d %H:%M")
            localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            # Format the event date and time
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()

            # Extract event details
            mainTitle = item.find('div', class_='content-now-title-schedule').get_text(strip=True)
            episodeTitle = item.find('div', class_='schedule-entry-episode-title')
            description = item.find('div', class_='schedule-entry-episode-desc')

            episodeTitle = episodeTitle.get_text(strip=True) if episodeTitle else ""
            description = description.get_text(strip=True) if description else ""

            # Construct the event content based on available data
            content = (
                f"{episodeTitle} - {description}" if episodeTitle and description
                else episodeTitle if episodeTitle
                else description if description
                else defaultDescription
            )

            # Append the processed event to the list
            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": mainTitle,
                "content": content,
            })

        # Sort the events by date and time
        return sorted(processedEvents, key=lambda x: (x["date"], x["hour"]))