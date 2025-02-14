from abc import ABC, abstractmethod
from datetime import datetime

class IChannelScraper(ABC):
    """
    Abstract base class that defines the structure for a channel scraper.
    Classes implementing this interface should define the scrapeProgramGuide method.
    """
    
    @abstractmethod
    def scrapeProgramGuide(self, startDate: datetime, numberOfDays: int, charReplacements: dict = None):
        """
        Scrapes the program guide for a channel, starting from the given date and covering the specified range of days.

        Args:
            startDate (datetime): The initial date from which the program guide scraping begins.
            numberOfDays (int): The number of days to scrape the program guide for.
            charReplacements (dict, optional): A dictionary of character replacements to apply to the program guide data.

        Returns:
            None
        """
        pass
