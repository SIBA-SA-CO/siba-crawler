import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime


class StartTvScraper(ScraperBase):
    """
    A scraper for extracting the TV program guide from Start TV.

    This class retrieves TV schedule data over a specified date range, processes it, 
    removes duplicates, and saves the formatted program guide.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the Start TV program guide for a specified date range.

        Args:
            startDate (str): The start date for scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to retrieve the program guide for.
            charReplacements (dict): A dictionary mapping characters to be replaced in the output data.

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
                dateKey = url.split('/')[-2]
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        
        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
