from src.scrapers.core.interfaces.ichannelscraper import IChannelScraper
from src.scrapers.core.urlgenerator import UrlGenerator
from src.scrapers.core.filewriter import FileWriter
from src.scrapers.core.logger import Logger

class ScraperBase(IChannelScraper):
    def __init__(self, channelConfig, urlFormatter, dataFetcher, dataProcessor, headers=None):
        """
        Base class for channel scrapers, providing common functionality for fetching,
        processing, and saving TV program data.

        Args:
            channelConfig (dict): Configuration settings for the channel, including the base URL.
            urlFormatter (IUrlFormatter): Instance responsible for formatting URLs based on dates.
            dataFetcher (IDataFetcher): Instance responsible for retrieving data from a URL.
            dataProcessor (IDataProcessor): Instance responsible for processing raw program data.
            headers (dict, optional): HTTP headers for the requests. Defaults to None.
        """
        self.channelConfig = channelConfig
        self.urlFormatter = urlFormatter
        self.dataProcessor = dataProcessor
        self.dataFetcher = dataFetcher  
        self.urlGenerator = UrlGenerator(channelConfig["url"], urlFormatter)  # Initializes the URL generator
        self.fileWriter = FileWriter(Logger())  # Initializes FileWriter with a logger
        self.headers = headers  # Use provided headers or default to None
        
    def getDataFromUrl(self, url: str):
        """
        Retrieves data from a given URL using the configured data fetcher.

        Args:
            url (str): The URL from which data should be fetched.

        Returns:
            dict or str: Parsed JSON data if applicable, otherwise raw text data.
        """
        return self.dataFetcher.fetchData(url, self.headers) if self.headers else self.dataFetcher.fetchData(url)
    
    def saveData(self, fileName: str, data: dict, charReplacements: dict, filePath: str):
        """
        Saves processed program data to a structured text file.

        Args:
            fileName (str): The name of the output file (without extension).
            data (dict): The processed program data to be saved.
            charReplacements (dict): Dictionary of character replacements to clean the data.
            filePath (str): Directory where the output file will be saved.
        """
        self.fileWriter.saveDataToTxt(fileName, data, charReplacements, filePath)
