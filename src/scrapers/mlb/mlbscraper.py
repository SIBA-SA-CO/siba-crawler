from src.scrapers.core.scraperbase import ScraperBase

class MlbScraper(ScraperBase):
    """
    A scraper for MLB program guides.

    This class retrieves the program guide from a specified URL, processes the 
    extracted data, applies character replacements, and saves the formatted 
    program schedule.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the MLB program guide for a given date range and processes the data.

        Args:
            startDate (str): The starting date for scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of consecutive days to retrieve the program guide for.
            charReplacements (dict): A dictionary mapping characters to be replaced in the processed data.

        Returns:
            None: The processed program guide is saved to a file.
        """

        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}
        dateKey = None
        url = self.channelConfig['url']
        dataFromUrl = self.getDataFromUrl(url)
        data = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
