from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover

class EwtnScraper(ScraperBase):
    """
    Scraper for extracting EWTN program guide data over a specified date range.
    
    This class utilizes the base scraper functionality to fetch, process, and save EWTN's
    TV schedule data, ensuring duplicate entries are removed before storage.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the EWTN program guide for a specified range of dates.

        Args:
            startDate (str): The starting date for scraping, in 'YYYY-MM-DD' format.
            numberOfDays (int): The number of days to scrape, including past and future dates.
            charReplacements (dict): A dictionary mapping characters to be replaced in the data.

        Returns:
            None
        """
        # Generate URLs for the specified date range
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        # Fetch and process data from each generated URL
        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey = url.split("/")[-2]  # Extract the date key from the URL
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        # Remove duplicate entries from the collected data
        data = DuplicateRemover.removeDuplicates(data)

        # Save the cleaned data to a file
        self.saveData(fileName, data, charReplacements, filePath)
