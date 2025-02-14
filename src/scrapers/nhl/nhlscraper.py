import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime


class NhlScraper(ScraperBase):
    """
    A scraper class to retrieve and process the NHL program guide.

    This class fetches schedule data for a given date range, processes the data 
    using a data processor, removes duplicate entries, and saves the final 
    program guide.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the NHL program guide over a specified date range.

        Args:
            startDate (str): The initial date to start scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of consecutive days to scrape the schedule for.
            charReplacements (dict): A dictionary of character replacements to apply to the processed data.

        Returns:
            None
        """
        # Generate URLs based on the provided date range
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        # Iterate over each URL and process the data
        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey=url.split("/")[-2]
                data[dateKey]=self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        
        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
