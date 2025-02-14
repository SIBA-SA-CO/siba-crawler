from datetime import datetime
from src.scrapers.core.scraperbase import ScraperBase

class HopeTvUrlFormatter:
    """
    Formats URLs for retrieving Hope TV program guide data.
    """

    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        """
        Constructs a formatted URL for a specific date.

        Args:
            targetDate (datetime): The target date for which data is to be retrieved.
            baseUrl (str): The base URL to which the formatted date will be appended.

        Returns:
            str: The formatted URL with the date appended.
        """
        dateStr = targetDate.strftime('%Y-%m-%d')
        return f"{baseUrl}{dateStr}T00%3A00%3A00-05%3A00"
