from src.scrapers.core.scraperbase import ScraperBase

class BvnTvScraper(ScraperBase):
    """
    A scraper class for retrieving and processing the program guide for Bvn Tv.

    This class scrapes program guide data over a specified date range, processes the data,
    and saves the final output to a file. It uses a URL generator to create URLs for each date
    and a data processor to format and filter the data.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict) -> None:
        """
        Scrapes the program guide for Bvn Tv over a range of days starting from the given date.

        Args:
            startDate (str): The initial date to start scraping, formatted as 'YYYY-MM-DD'.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict): A dictionary of character replacements to apply to the data
                                   before saving. For example, replacing special characters.

        Returns:
            None: The processed data is saved to a file instead of being returned.
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
                dateKey = url.split("/")[-2]  # Extract the date key from the URL
                data[dateKey] = self.dataProcessor.processData(dataFromUrl, defaultSynopsis, dateKey)

        # Save the processed data to a file
        self.saveData(fileName, data, charReplacements, filePath)