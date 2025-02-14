from src.scrapers.core.duplicateremover import DuplicateRemover
from src.scrapers.core.scraperbase import ScraperBase

class BeinSportsScraper(ScraperBase):
    """
    A class to scrape the program guide for Bein Sports over a specified date range.

    This class generates URLs for the given date range, retrieves data from those URLs,
    processes the data to remove duplicates, and saves the final output.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the program guide for Bein Sports over a range of days starting from the given date.

        Args:
            startDate (str): The initial date to start scraping, in the format 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict): A dictionary of character replacements to apply to the data.

        Returns:
            None
        """
        # Generate URLs based on the provided date range
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        # Set up headers for the HTTP requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        # Iterate over each URL and process the data
        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey = url.split("T")[1][-10:]
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        # Remove duplicates from the data
        data = DuplicateRemover.removeDuplicates(data)

        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)