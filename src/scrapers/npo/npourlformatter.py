from src.scrapers.core.interfaces.iurlformatter import IUrlFormatter
from datetime import datetime

class NpoUrlFormatter(IUrlFormatter):
    """
    A URL formatter for generating NPO program guide URLs.

    This class formats URLs by appending a date parameter to the base URL, 
    ensuring that data for a specific date can be retrieved.
    """

    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        """
        Generates a formatted URL with the specified date.

        Args:
            targetDate (datetime): The date for which the data will be retrieved.
            baseUrl (str): The base URL to which the formatted date will be appended.

        Returns:
            str: The complete URL including the formatted date parameter.
        """
        return f"{baseUrl}{targetDate.strftime('%d-%m-%Y')}&guid="
