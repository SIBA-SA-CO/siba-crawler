from .interfaces.iurlformatter import IUrlFormatter
from datetime import datetime

class TitanTvUrlFormatter(IUrlFormatter):
    """
    URL formatter for Titan TV that generates a list of URLs for each hour of a given date.

    This class constructs URLs by appending formatted date and hour parameters to the base URL,
    ensuring coverage of all 24 hours in a specified day.
    """

    def formatUrl(self, targetDate: datetime, baseUrl: str) -> list:
        """
        Generates a list of URLs for each hour of the specified date.

        Args:
            targetDate (datetime): The date for which URLs will be generated.
            baseUrl (str): The base URL, which will be modified with date and time parameters.

        Returns:
            list: A list of formatted URLs covering each hour of the target date.
        """
        formattedUrls = []  # List to store generated URLs

        # Extract components of the base URL
        urlParts = baseUrl.split("/")
        baseUrlPrefix = "/".join(urlParts[:7]) + "/"  # Base URL section
        extraPath = "/" + "/".join(urlParts[8:])  # Remaining path after date/hour

        # Format the target date as YYYYMMDD
        formattedDate = targetDate.strftime('%Y%m%d')

        # Generate a URL for each hour (00:00 to 23:00)
        for hour in range(24):
            formattedHour = f"{hour:02}00"  # Format hour as HHMM
            formattedUrl = f"{baseUrlPrefix}{formattedDate}{formattedHour}{extraPath}"
            formattedUrls.append(formattedUrl)

        return formattedUrls
