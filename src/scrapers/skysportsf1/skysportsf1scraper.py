from src.scrapers.core.duplicateremover import DuplicateRemover
from src.scrapers.core.scraperbase import ScraperBase


class SkySportsF1Scraper(ScraperBase):
    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig["defaultDescription"]
        fileName = self.channelConfig["fileName"]
        filePath = self.channelConfig["outputPath"]
        data = {}

        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey = url.split("date=")[-1]
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        self.saveData(fileName, data, charReplacements, filePath)

