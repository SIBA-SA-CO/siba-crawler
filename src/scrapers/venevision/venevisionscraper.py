from src.scrapers.core.scraperbase import ScraperBase

class VeneVisionScraper(ScraperBase):
    """
    A scraper class for extracting the program guide from the Venevisión website.

    This class retrieves the program schedule, processes the data, and saves it
    in the specified format.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the program guide for Venevisión over a range of days starting from the given date.

        Args:
            startDate (str): The initial date to start scraping, in the format 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict): A dictionary mapping characters to be replaced in the data.

        Returns:
            None
        """
        # Retrieve configuration settings
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        url = self.channelConfig['url']

        # Fetch raw data from the website
        dataFromUrl = self.getDataFromUrl(url)

        # Process the extracted data
        data = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, targetDate=None)

        # Save the processed data to a file
        self.saveData(fileName, data, charReplacements, filePath)

