import requests
from src.scrapers.core.interfaces.idatafetcher import IDataFetcher

class HttpClient(IDataFetcher):
    """
    Class for handling HTTP requests.
    """

    def __init__(self, logger):
        self.logger = logger

    def fetchData(self, url, headers=None):
        """
        Makes a GET request to the specified URL.

        Args:
            url (str): The URL to send the request to.
            headers (dict, optional): A dictionary of HTTP headers to include in the request.

        Returns:
            dict or str: The response content in JSON format if applicable, otherwise text.
        """
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an exception for unsuccessful responses
            self.logger.logInfo(f"Successfully retrieved data from {url}")
            return response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text
        except requests.RequestException as requestError:
            self.logger.logError(f"Error retrieving data from {url}: {requestError}")
            return None
