from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover

class HopeTvScraper(ScraperBase):
    """
    Scrapes and processes Hope TV program guide data over a given date range.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes and processes the program guide for Hope TV.

        Args:
            startDate (str): Initial date for scraping in 'YYYY-MM-DD' format.
            numberOfDays (int): Number of days to scrape.
            charReplacements (dict): Character replacements to apply to the data.

        Returns:
            None
        """
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey = url.split("day=")[-1].split("T")[0]
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        self.saveData(fileName, data, charReplacements, filePath)
