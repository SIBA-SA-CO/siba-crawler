import pytz
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class UlfnDataProcessor(IDataProcessor):
    """
    Processes ULFN program schedule data and organizes events by date.

    This class extracts event details such as title, description, and start time 
    from raw HTML data. It converts times to a 24-hour format, adjusts for time zones, 
    and structures the data into a list of scheduled events.
    """

    initialDate = None  # Start date for processing the schedule
    daysRange = None  # Number of days to consider in the schedule

    def __init__(self, timezone: str):
        """
        Initializes the data processor with the source timezone.

        Args:
            timezone (str): The source timezone of the events.
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def convertTo24Hour(self, timeStr: str) -> str:
        """
        Converts a given time string from 12-hour format (AM/PM) to 24-hour format.

        Special cases such as "NOON" and "MIDNIGHT" are handled separately.

        Args:
            timeStr (str): The time string in 12-hour format, possibly containing "ET".

        Returns:
            str: The converted time string in 24-hour format (HH:MM).
        """
        timeStr = timeStr.replace("ET", "").strip()

        if "NOON" in timeStr:
            return "12:00"
        if "MIDNIGHT" in timeStr:
            return "00:00"

        try:
            timeObj = datetime.strptime(timeStr, "%I:%M %p")
        except ValueError:
            timeObj = datetime.strptime(timeStr, "%I %p")

        return timeObj.strftime("%H:%M")

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        """
        Processes raw HTML schedule data and extracts relevant event details.

        The method organizes events by weekdays, Saturdays, and Sundays, assigns 
        appropriate time zone conversions, and generates a structured event list.

        Args:
            rawData (str): The raw HTML content of the schedule page.
            defaultDescription (str): Default description to use if no specific content is found.
            targetDate (str): The target date for processing events (YYYY-MM-DD).

        Returns:
            list: A sorted list of processed event dictionaries, each containing:
                - "date" (str): Event date in "YYYY-MM-DD" format.
                - "hour" (str): Event start time in "HH:MM" 24-hour format.
                - "title" (str): Event title.
                - "content" (str): Event description or default text.
        """
        scheduleByDayType = {
            'Weekdays(Eastern Time)Updates': [],
            'Saturday (Eastern Time)': [],
            'Sunday (Eastern Time)': []
        }
        processedData = []

        soup = BeautifulSoup(rawData, 'html.parser')
        scheduleSections = soup.find_all('div', class_='wp-block-column')

        # Generate date range for processing
        initialDate = datetime.strptime(self.initialDate, "%Y-%m-%d")
        dateRange = [initialDate + timedelta(days=i) for i in range(-self.daysRange, self.daysRange + 1)]

        # Extract schedule by day type
        for section in scheduleSections:
            dayType = section.find('h2').get_text(strip=True)
            scheduleItems = section.find_all('p')

            for item in scheduleItems:
                text = item.get_text(strip=True)
                if "–" in text:
                    time, program = text.split("–", 1)
                    time24Hr = self.convertTo24Hour(time.strip())
                    scheduleByDayType[dayType].append({
                        'hour': time24Hr,
                        'title': program.strip(),
                        'content': defaultDescription
                    })

        # Assign events to correct dates
        for date in dateRange:
            if date.weekday() < 5:
                dayType = 'Weekdays(Eastern Time)Updates'
            elif date.weekday() == 5:
                dayType = 'Saturday (Eastern Time)'
            elif date.weekday() == 6:
                dayType = 'Sunday (Eastern Time)'

            for item in scheduleByDayType[dayType]:
                startTimeObj = datetime.strptime(f"{date.strftime('%Y-%m-%d')} {item['hour']}", "%Y-%m-%d %H:%M")
                localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
                eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
                eventTime = targetEventDatetime.strftime("%H:%M").strip()

                processedData.append({
                    'date': eventDate,
                    'hour': eventTime,
                    'title': item['title'],
                    'content': item['content'],
                })

        # Sort events by date and time
        sortedEvents = sorted(
            processedData,
            key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), datetime.strptime(x["hour"], "%H:%M"))
        )

        return sortedEvents
