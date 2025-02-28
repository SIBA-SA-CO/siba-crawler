import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime

class WarnerScraper(ScraperBase):
    """
    Scraper class for extracting program guide data from Warner channels' web pages.

    This scraper iterates over configured sub-channels, fetches their schedule data from 
    the provided URLs, processes it using a data processor, and saves the final structured data.

    Inherits from:
        ScraperBase: Base scraper class providing common scraping functionality.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the program guide for all configured sub-channels, processes the data, 
        and saves it to files.

        Args:
            startDate (str): Starting date for the program guide (unused in current implementation).
            numberOfDays (int): Number of days to scrape (unused in current implementation).
            charReplacements (dict): Dictionary of character replacements to apply when saving data files.

        This method does the following:
            - Builds URLs for each sub-channel by replacing the placeholder in the base URL.
            - Fetches raw schedule data from each URL.
            - Processes the raw data into structured program data using the configured data processor.
            - Saves the processed data to files in the specified output path.
        """
        filePath = self.channelConfig['outputPath']
        baseUrl = self.channelConfig['url']
        data = {}
        dateKey = None

        # Loop through each configured sub-channel to fetch and process data
        for channel in self.channelConfig['subChannels']:
            channelName = channel.get("fileName")
            clientId = channel.get("id")
            defaultSynopsis = channel.get('defaultDescription')

            # Build channel-specific URL
            clientUrl = baseUrl.replace("HLN", clientId)

            # Fetch data from URL
            dataFromUrl = self.getDataFromUrl(clientUrl)

            # Process data if successfully retrieved
            if dataFromUrl:
                programs = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)
                if programs:
                    data[channelName] = programs

        # Save processed data to files
        for channelName, programData in data.items():
            self.saveData(channelName, programData, charReplacements, filePath)
