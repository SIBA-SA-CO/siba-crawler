from src.scrapers.core.scraperbase import ScraperBase


class ExtasyScraper(ScraperBase):
    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        defaultSynopsis = self.channelConfig["defaultDescription"]
        fileName = self.channelConfig["fileName"]
        filePath = self.channelConfig["outputPath"]
        url = self.channelConfig["url"]

        dataFromUrl = self.getDataFromUrl(url)
        data = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, None)
        self.saveData(fileName, data, charReplacements, filePath)
