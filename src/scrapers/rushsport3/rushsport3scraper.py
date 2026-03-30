from src.scrapers.core.scraperbase import ScraperBase


class RushSport3Scraper(ScraperBase):
    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict) -> None:
        defaultSynopsis = self.channelConfig["defaultDescription"]
        fileName = self.channelConfig["fileName"]
        filePath = self.channelConfig["outputPath"]

        rawData = self.dataFetcher.fetchData()

        if rawData is None or rawData.empty:
            return

        data = self.dataProcessor.processData(rawData, defaultSynopsis, targetDate="")
        self.saveData(fileName, data, charReplacements, filePath)
