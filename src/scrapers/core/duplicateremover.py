class DuplicateRemover:
    """Handles duplicate removal from hierarchical or flat data structures."""

    @staticmethod
    def removeDuplicates(data: dict) -> dict:
        """
        Removes duplicate entries from a nested dictionary (e.g., TV programs).

        Args:
            data (dict): The data structure (nested dictionary) containing program data.

        Returns:
            dict: The updated dictionary with duplicates removed.
        """
        seen = set()
        filteredData = {}
        for keyName, programData in data.items():
            uniqueData = []

            for program in programData:
                eventDate = program.get("date").strip()
                eventHour = program.get("hour").strip()
                uniqueKey = (eventDate, eventHour)
    
                if uniqueKey  not in seen:
                    seen.add(uniqueKey)
                    uniqueData.append(program)

            if uniqueData:
                filteredData[keyName] = uniqueData
        return filteredData
