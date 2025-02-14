from src.scrapers.core.scraperbase import ScraperBase

class GameShowNetworkScraper(ScraperBase):
    """
    Scraper for Game Show Network, retrieving and processing program guide data.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        """
        Scrapes and processes the Game Show Network program guide.

        Args:
            startDate (str): The starting date for scraping (format: 'YYYY-MM-DD').
            numberOfDays (int): Number of days to retrieve the program guide for.
            charReplacements (dict): Dictionary of character replacements for processing data.

        Returns:
            None
        """
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']
        url = self.channelConfig['url']
        dataFromUrl = self.getDataFromUrl(url)
        data = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, None)

        # Save the processed data
        self.saveData(fileName, data, charReplacements, filePath)
