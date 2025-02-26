import re
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover
from playwright.sync_api import sync_playwright
from src.scrapers.core.logger import Logger
from time import sleep
from datetime import datetime


class WarnerScraper(ScraperBase):
    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):

        # Generate URLs based on the provided date range
        filePath = self.channelConfig['outputPath']
        baseUrl = self.channelConfig['url']
        data = {}
        dateKey = None

        # Iterate over each URL and process the data

        for channel in self.channelConfig['subChannels']:
            channelName = channel.get("fileName")
            clientId =  channel.get("id")
            defaultSynopsis = channel.get('defaultDescription')
            clientUrl = baseUrl.replace("HLN", clientId)
            dataFromUrl = self.getDataFromUrl(clientUrl)
            if dataFromUrl:
                programs = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)
                if programs:
                    data[channelName] = programs
                    
        # Save the processed data
        for channelName, programData in data.items():
            self.saveData(channelName, programData, charReplacements,filePath)
