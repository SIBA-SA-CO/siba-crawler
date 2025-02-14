import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime


class NpoScraper(ScraperBase):
    """
    A scraper class for retrieving and processing the NPO program guide.

    This class generates URLs for a given date range, fetches program data for 
    multiple sub-channels, processes it, and saves the structured output.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the NPO program guide over a specified date range.

        Args:
            startDate (str): The start date for scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of consecutive days to retrieve program data for.
            charReplacements (dict): A dictionary mapping characters to be replaced in the output data.

        Returns:
            None: The processed data is saved to the specified output path.
        """
        # Generate URLs based on the provided date range
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        filePath = self.channelConfig['outputPath']
        data = {}
        dateKey = None

        # Iterate over each URL and process the data
        for url in urls:
            for channel in self.channelConfig['subChannels']:
                channelName = channel.get("fileName")
                clientId =  channel.get("id")
                defaultSynopsis = channel.get('defaultDescription')
                clientUrl = f"{url}{clientId}"
                dataFromUrl = self.getDataFromUrl(clientUrl)
                if dataFromUrl:
                    programs = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)
                    if channelName in data:
                        data[channelName].extend(programs)
                    else:
                        data[channelName] = programs

        data = DuplicateRemover.removeDuplicates(data)
        # Save the processed data
        for channelName, programData in data.items():
            self.saveData(channelName, programData, charReplacements,filePath)
