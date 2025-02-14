from datetime import datetime
from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover

class My9Scraper(ScraperBase):
    """
    A scraper for extracting and processing the TV program guide for My9.

    This class retrieves schedule data from multiple URLs, processes it using a data processor, 
    removes duplicate entries, and saves the final structured data.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes and processes the program guide for My9 over a specified date range.

        This method generates URLs based on the given date range, extracts and processes 
        schedule data from each URL, removes duplicate entries, and saves the final 
        structured data.

        Args:
            startDate (str): The starting date for scraping in 'YYYY-MM-DD' format.
            numberOfDays (int): The number of consecutive days to scrape.
            charReplacements (dict): A dictionary of character replacements to apply when saving the data.

        Returns:
            None
        """
        # Generate URLs based on the provided date range
        urls = self.urlGenerator.getDateUrls(startDate, numberOfDays)
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        # Iterate over each URL and process the data
        for url in urls:
            dataFromUrl = self.getDataFromUrl(url)
            if dataFromUrl:
                dateKey = url.split("/")[-4][0:8]
                dateKey = datetime.strptime(dateKey, "%Y%m%d").strftime("%Y-%m-%d")
                programs = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)
                if dateKey in data:
                    data[dateKey].extend(programs)
                else:
                    data[dateKey] = programs

        data = DuplicateRemover.removeDuplicates(data)

        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
