from datetime import datetime
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover

class Fox19NowScraper(ScraperBase):
    """
    Scrapes and processes the FOX19 Now program guide over a specified date range.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the program guide for FOX19 Now over a range of days starting from the given date.

        Args:
            startDate (str): The initial date to start scraping, in the format 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict): A dictionary of character replacements to apply to the data.

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
                dateKey = url.split("/")[-4][:8]
                dateKey = datetime.strptime(dateKey, "%Y%m%d").strftime("%Y-%m-%d")
                programs = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)
                data.setdefault(dateKey, []).extend(programs)

        data = DuplicateRemover.removeDuplicates(data)
        self.saveData(fileName, data, charReplacements, filePath)
