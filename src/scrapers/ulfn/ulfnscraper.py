from src.scrapers.core.scraperbase import ScraperBase

class UlfnScraper(ScraperBase):
    """
    Scraper for extracting and processing the ULFN program guide.

    This class retrieves schedule data from a predefined URL, processes the 
    extracted information using a data processor, and saves the formatted data 
    in the specified output location.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes the ULFN program guide over a specified date range.

        The method fetches program schedule data from a configured URL, processes 
        it using the associated data processor, and saves the structured data.

        Args:
            startDate (str): The initial date to start scraping, in the format 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict): A dictionary of character replacements to apply to the data.

        Returns:
            None
        """
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        data = {}

        # Retrieve program data from the configured URL
        url = self.channelConfig['url']
        dataFromUrl = self.getDataFromUrl(url)

        # Configure the data processor with the date range
        self.dataProcessor.initialDate = startDate
        self.dataProcessor.daysRange = numberOfDays

        # Process the retrieved data
        data = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, None)

        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
