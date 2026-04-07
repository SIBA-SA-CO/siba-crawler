from datetime import datetime

from src.scrapers.core.duplicateremover import DuplicateRemover
from src.scrapers.core.scraperbase import ScraperBase


class RtpMundoScraper(ScraperBase):
    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict) -> None:
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig["defaultDescription"]
        fileName = self.channelConfig["fileName"]
        filePath = self.channelConfig["outputPath"]
        data = {}

        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if not dataFromUrl:
                continue

            targetDate = self._extractTargetDate(url)
            data[targetDate] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, targetDate)

        data = DuplicateRemover.removeDuplicates(data)
        self.saveData(fileName, data, charReplacements, filePath)

    def _extractTargetDate(self, url: str) -> str:
        rawDate = url.rstrip("/").split("/")[-1]
        return datetime.strptime(rawDate, "%d-%m-%Y").strftime("%Y-%m-%d")

