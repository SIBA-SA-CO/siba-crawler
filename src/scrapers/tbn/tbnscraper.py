import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime


class TbnScraper(ScraperBase):
    """
    A web scraper for extracting the TBN program guide.

    This class retrieves TV schedule data from TBN over a specified date range, 
    processes it using a data processor, and saves the structured data.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes and processes the TBN program guide for a specified date range.

        Args:
            startDate (str): The start date for scraping, in the format 'YYYY-MM-DD'.
            numberOfDays (int): The number of consecutive days to retrieve schedule data.
            charReplacements (dict): A dictionary mapping characters to be replaced 
                                     in the extracted data.

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
                dateKey = url.split("/")[-2]
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        
        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
