import re
from datetime import datetime, timedelta
from src.scrapers.core.interfaces.iurlformatter import IUrlFormatter

class BetUrlFormatter(IUrlFormatter):
    """
    A class to format URLs for Bein Sports data requests.

    This class generates a URL to retrieve events based on the specified date range.
    It takes a date and formats it into a URL query string for the API request.
    """

    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        """
        Formats a URL using the provided date and base URL.

        Args:
            targetDate (datetime): The date to be included in the formatted URL.
            baseUrl (str): The base URL to which the date will be appended.

        Returns:
            str: The formatted URL, with the date appended to the base URL.
        """
        return f"{baseUrl}{targetDate.strftime('%Y%m%d')}/"

    
