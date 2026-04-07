import time

import requests

from src.scrapers.core.interfaces.idatafetcher import IDataFetcher


class SkySportsF1DataFetcher(IDataFetcher):
    def __init__(self, logger):
        self.logger = logger
        self.timeout = 20
        self.maxRetries = 3
        self.defaultHeaders = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            )
        }

    def fetchData(self, url, headers=None):
        requestHeaders = dict(self.defaultHeaders)
        if headers:
            requestHeaders.update(headers)

        for attempt in range(1, self.maxRetries + 1):
            try:
                self.logger.logInfo(f"Attempt {attempt}/{self.maxRetries}: Fetching {url}")
                response = requests.get(url, headers=requestHeaders, timeout=self.timeout)
                response.raise_for_status()
                self.logger.logInfo(f"Successfully retrieved data from {url}")
                return response.text
            except requests.RequestException as requestError:
                self.logger.logError(
                    f"Error retrieving data from {url} (Attempt {attempt}/{self.maxRetries}): {requestError}"
                )
                if attempt < self.maxRetries:
                    time.sleep(attempt)

        return None
