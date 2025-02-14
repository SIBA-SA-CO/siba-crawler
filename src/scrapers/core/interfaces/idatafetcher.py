from abc import ABC, abstractmethod

class IDataFetcher(ABC):
    """
    Abstract base class for a data fetcher.
    Classes implementing this interface should define the fetchData method.
    """
    
    @abstractmethod
    def fetchData(self, url: str):
        """
        Fetches data from the specified URL.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            None
        """
        pass