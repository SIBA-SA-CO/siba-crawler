import re
from time import sleep
from playwright.sync_api import sync_playwright
from src.scrapers.core.interfaces.idatafetcher import IDataFetcher
from src.scrapers.core.logger import Logger
from datetime import datetime

class MeTvToonsDataFetcher(IDataFetcher):
    def __init__(self, logger: Logger):
        """
        Initializes the data fetcher with a logger instance.

        Args:
            logger (Logger): An instance of the Logger class for logging errors and messages.
        """
        self.logger = logger

    def fetchData(self, url):
        """
        Scrapes schedule data from the specified URL and extracts show details.

        Args:
            url (str): The webpage URL containing the schedule data.

        Returns:
            list: A list of tuples containing extracted show data in the format:
                  (date, show_time, show_title, episode_title, description)
        """
        eventDataList = []
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, slow_mo=500)
            page = browser.new_page()
            page.goto(url)
            date = url.split('/')[-2]

            try:
                containerXPath = '//*[@id="schedule_container"]'
                page.wait_for_selector(f'xpath={containerXPath}', timeout=5000)
                container = page.locator(f'xpath={containerXPath}')

                currentShowWrapper = container.locator('section.current-show-wrapper')
                hasCurrentShow = currentShowWrapper.count() >= 1 

                if hasCurrentShow:
                    currentEvent = currentShowWrapper.first
                    rawShowTime = self.getTextIfExists(currentEvent, '.sched-show-title')
                    rawShowTime = rawShowTime[-10:].strip()
                    showTime = self.formatTime(rawShowTime)
                    showTitle = self.getTextIfExists(currentEvent, '.current-show-title')
                    episodeTitle = self.getTextIfExists(currentEvent, '.current-episode-title')
                    description = self.getTextIfExists(currentEvent, 'p')
                    eventDataList.append((date, showTime, showTitle, episodeTitle, description))

                scheduledEvents = container.locator('div.sched-item')
                eventCount = scheduledEvents.count()

                if eventCount >= 1:
                    for i in range(eventCount):
                        event = scheduledEvents.nth(i)
                        rawShowTime = self.getTextIfExists(event, '.sched-show-time')
                        showTime = self.formatTime(rawShowTime)
                        showTitle = self.getTextIfExists(event, '.sched-show-name')
                        episodeTitle = self.getTextIfExists(event, '.sched-episode-title')
                        description = self.getTextIfExists(event, 'p')
                        eventDataList.append((date, showTime, showTitle, episodeTitle, description))
            
            except TimeoutError:
                self.logger.logError("Timeout occurred while fetching data from MeTvToons. The schedule page may be unresponsive or have changed structure.")
            
            browser.close()
            return eventDataList

    def getTextIfExists(self, locator, selector, timeout=500) -> str:
        """
        Extracts text from an element if it exists; otherwise, returns a default value.

        Args:
            locator: The locator object used to find the element.
            selector (str): The CSS selector for the element to be extracted.
            timeout (int, optional): The maximum time to wait for the element, in milliseconds. Defaults to 500.

        Returns:
            str: The text content of the element, or 'n/a' if not found.
        """
        try:
            element = locator.locator(selector).first
            if element.count() > 0:
                return element.text_content(timeout=timeout).strip()
            return "n/a"
        except TimeoutError:
            return "Not available"

    def formatTime(self, timeText):
        """
        Converts a time string from the format '6:00am ET' to 'HH:MM' in 24-hour format.

        Args:
            timeText (str): The raw time string to be formatted.

        Returns:
            str: The formatted time in 'HH:MM' format, or 'Invalid time' if conversion fails.
        """
        match = re.match(r"(\d{1,2}:\d{2})(am|pm)", timeText.lower())
        if match:
            timeStr, period = match.groups()
            timeObj = datetime.strptime(timeStr + period, "%I:%M%p")
            return timeObj.strftime("%H:%M")
        return "Invalid time"