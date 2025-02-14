from time import sleep
from playwright.sync_api import sync_playwright
from src.scrapers.core.interfaces.idatafetcher import IDataFetcher
from src.scrapers.core.logger import Logger

class HopeTvDataFetcher(IDataFetcher):
    """
    Fetches schedule data from Hope TV using Playwright with retry logic.
    """

    def __init__(self, logger: Logger):
        """
        Initializes the data fetcher with a logger instance.

        Args:
            logger (Logger): Logger instance for logging messages.
        """
        self.logger = logger

    def fetchData(self, url):
        """
        Retrieves schedule data from the specified Hope TV URL with retry logic.

        Args:
            url (str): The target URL to fetch schedule data from.

        Returns:
            list: A list of schedule items if successful, otherwise an empty list.
        """
        scheduleResponses = []
        retries = 3
        wait_time = 2

        for attempt in range(retries):
            try:
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True, slow_mo=500)
                    page = browser.new_page()

                    def handleResponse(response):
                        if "schedule" in response.url:
                            try:
                                jsonData = response.json()
                                if "items" in jsonData:
                                    scheduleResponses.extend(jsonData["items"])
                            except Exception as error:
                                self.logger.logError(f"Error parsing JSON response: {error}")

                    page.on("response", handleResponse)

                    self.logger.logInfo(f"Attempt {attempt + 1}/{retries}: Fetching {url}")
                    page.goto(url, timeout=30000)  # Timeout set to 30 seconds
                    page.wait_for_load_state("networkidle")

                    browser.close()

                    if scheduleResponses:
                        return scheduleResponses  # Return if data is obtained
            
            except Exception as e:
                self.logger.logError(f"Error fetching data (Attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    sleep(wait_time)  # Wait before retrying

        self.logger.logError(f"Failed to fetch data after {retries} attempts.")
        return []  # Return an empty list if all attempts fail
