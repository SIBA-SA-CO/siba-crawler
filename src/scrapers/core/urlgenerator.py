from datetime import datetime, timedelta
from .interfaces.iurlformatter import IUrlFormatter

class UrlGenerator:
    """
    Generates URLs for a given date range using a specified URL formatter.

    This class takes a base URL and a formatter, then generates a list of URLs
    covering a configurable range of days before and after a given initial date.
    """

    def __init__(self, baseUrl: str, formatter: IUrlFormatter):
        """
        Initializes the UrlGenerator with a base URL and a formatter.

        Args:
            baseUrl (str): The base URL used for generating formatted URLs.
            formatter (IUrlFormatter): The formatter responsible for structuring URLs.
        """
        self.baseUrl = baseUrl
        self.formatter = formatter

    def getDateUrls(self, initialDateStr: str, daysRange: int = 15) -> list[str]:
        """
        Generates a list of URLs for a specified date range.

        Args:
            initialDateStr (str): The starting date as a string in 'YYYY-MM-DD' format.
            daysRange (int, optional): The number of days before and after the initial date
                                      to generate URLs for. Defaults to 15.

        Returns:
            list[str]: A list of formatted URLs covering the specified date range.
        """
        initialDate = datetime.strptime(initialDateStr, "%Y-%m-%d")
        dates = [
            initialDate + timedelta(days=i)
            for i in range(-daysRange, daysRange + 1)
        ]
        urls = []
        for date in dates:
            formattedUrl = self.formatter.formatUrl(date, self.baseUrl)
            if isinstance(formattedUrl, list):
                urls.extend(formattedUrl)
            else:
                urls.append(formattedUrl)
        return urls
