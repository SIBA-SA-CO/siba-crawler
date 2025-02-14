from abc import ABC, abstractmethod
from datetime import datetime

class IDataProcessor(ABC):
    """
    Abstract base class for data processors.

    This class defines an interface for processing event data, requiring
    implementation of the `processData` method to extract and format event details.
    """

    @abstractmethod
    def processData(self, data: dict, defaultSynopsis: str, dateKey: str = None) -> list:
        """
        Abstract method to process event data.

        Args:
            data (dict): The raw data containing event information.
            defaultSynopsis (str): A default description to use if no specific data is available.
            dateKey (str, optional): The key used to identify the event date. Defaults to None.

        Returns:
            list: A list of processed events with extracted details.
        """
        pass