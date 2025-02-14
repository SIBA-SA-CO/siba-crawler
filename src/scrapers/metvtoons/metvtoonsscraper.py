from src.scrapers.core.scraperbase import ScraperBase
from src.scrapers.core.duplicateremover import DuplicateRemover

class MeTvToonsScraper(ScraperBase):
    """
    A scraper for retrieving and processing the MeTV Toons program guide.

    This class fetches schedule data over a specified date range, processes 
    it using a data processor, applies character replacements, and saves the 
    formatted data to an output file.

    Methods:
        scrapeProgramGuide(startDate, numberOfDays, charReplacements):
            Scrapes and processes the program guide for the given date range.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the MeTV Toons program guide for a specified date range.

        This method generates URLs for the given date range, fetches schedule 
        data, processes it, removes duplicates, and saves the final data.

        Args:
            startDate (str): The initial date for scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the schedule for.
            charReplacements (dict): A dictionary mapping characters to be replaced 
                                     in the extracted data.

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
                dateKey=url.split("/")[-2]
                data[dateKey]=self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        data = DuplicateRemover.removeDuplicates(data)
        
        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
