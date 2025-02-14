import re
from datetime import datetime, timedelta
from src.scrapers.core.interfaces.iurlformatter import IUrlFormatter

class BeinSportsUrlFormatter(IUrlFormatter):
    """
    A class to format URLs for Bein Sports data requests.

    This class generates a URL to retrieve events based on the specified date range.
    It takes a date and formats it into a URL query string for the API request.
    """

    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        """
        Formats a URL to retrieve events for the given date range.

        Args:
            targetDate (datetime): The target date to filter events.
            baseUrl (str): The base URL for the API endpoint.

        Returns:
            str: The formatted URL to request events within the given date range.
        """
        # Calculate the date range for the event request
        startDateTime = (targetDate + timedelta(days=1)).strftime('%Y-%m-%d')
        endDateTime = targetDate.strftime('%Y-%m-%d')
        newUrl = re.sub(r'startBefore=\d{4}-\d{2}-\d{2}', f'startBefore={startDateTime}', baseUrl)
        newUrl = re.sub(r'endAfter=\d{4}-\d{2}-\d{2}', f'endAfter={endDateTime}', newUrl)
        return newUrl

    
