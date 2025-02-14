from abc import ABC, abstractmethod
from datetime import datetime

class IUrlFormatter(ABC):
    """
    Abstract base class that defines the structure for a URL formatter.
    Classes implementing this interface should define the format_url method.
    """
    
    @abstractmethod
    def formatUrl(self, date: datetime, baseUrl: str) -> str:
        """
        Formats a URL based on the provided date and base URL.

        Args:
            date (datetime): The date to be included in the formatted URL.
            baseUrl (str): The base URL to which the date will be appended.

        Returns:
            str: The formatted URL string.
        """
        pass