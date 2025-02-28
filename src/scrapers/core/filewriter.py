import os
import re

class FileWriter:
    """
    Class to handle file writing operations.
    """

    def __init__(self, logger):
        """
        Initializes the FileWriter.

        Args:
            logger: Logger instance to log info and errors.
        """
        self.logger = logger

    def writeProgramData(self, file, program, currentDate, charReplacements=None):
        """
        Writes program data to a text file, truncating title if it exceeds 120 characters.

        Args:
            file: The open file object where data will be written.
            program (dict): A dictionary containing the program data.
            currentDate (str): The current date to write in the file.
            charReplacements (dict, optional): A dictionary of character replacements.

        Returns:
            str: The updated current date if it changes.
        """
        date = program.get('date', '')
        hour = program.get('hour', '')
        title = program.get('title', '').strip()
        content = program.get('content', '').strip()

        # Apply character replacements if provided
        if charReplacements:
            for oldChar, newChar in charReplacements.items():
                title = title.replace(oldChar, newChar)
                content = content.replace(oldChar, newChar)

        title = re.sub(r'-{2,}', '-', title)
        content = re.sub(r'-{2,}', '-', content)

        title = title.strip("-")
        content = content.strip("-")

        # Truncate title if it exceeds 120 characters
        if len(title) > 120:
            title = title[:120]

        # Write the date only if it changes
        if date != currentDate:
            currentDate = date
            file.write(f"{currentDate}\n")

        # Write program data
        file.write(f"{hour}---{title}---{content}---USA|TV-PG---SIBA_TIPO|UNICO--- --- --- --- --- ---SIN_CTI|{content}--- --- --- ---\n")

        return currentDate

    def saveDataToTxt(self, channelName, programData, charReplacements=None, filePath='./data'):
        """
        Saves channel data to a text file.

        Args:
            channelName (str): The name of the channel.
            programData (dict or list): Program data (either a list or a dictionary).
            charReplacements (dict, optional): Optional character replacements.
            filePath (str, optional): The base path where the file will be saved.

        Returns:
            None
        """
        # Create the channel folder if it doesn't exist
        channelFolder = os.path.join(filePath)
        os.makedirs(channelFolder, exist_ok=True)

        # Generate the file name
        fileName = f"{channelName}.txt"
        fullFilePath = os.path.join(channelFolder, fileName)

        try:
            with open(fullFilePath, 'w', encoding='utf-8') as file:
                currentDate = None

                # If programData is a dictionary
                if isinstance(programData, dict):
                    for date, programs in programData.items():
                        for program in programs:
                            currentDate = self.writeProgramData(file, program, currentDate, charReplacements)

                # If programData is a list (individual programs)
                elif isinstance(programData, list):
                    for program in programData:
                        currentDate = self.writeProgramData(file, program, currentDate, charReplacements)

                else:
                    self.logger.logError("The format of programData is invalid. It should be either a dictionary or a list.")
                    return

            self.logger.logInfo(f"File generated for {channelName}: {fullFilePath}")

        except Exception as e:
            self.logger.logError(f"Error saving data to the file {fullFilePath}: {e}")
