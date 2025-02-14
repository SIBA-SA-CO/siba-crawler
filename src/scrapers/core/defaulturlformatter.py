from .interfaces.iurlformatter import IUrlFormatter
from datetime import datetime

class DefaultUrlFormatter(IUrlFormatter):
    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        """
        Formats a URL using the provided date and base URL.

        Args:
            targetDate (datetime): The date to be included in the formatted URL.
            baseUrl (str): The base URL to which the date will be appended.

        Returns:
            str: The formatted URL, with the date appended to the base URL.
        """
        return f"{baseUrl}{targetDate.strftime('%Y-%m-%d')}/"