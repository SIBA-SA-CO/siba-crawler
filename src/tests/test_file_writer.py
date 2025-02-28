import pytest
import os
from unittest.mock import MagicMock
from src.scrapers.core.filewriter import FileWriter

@pytest.fixture
def fileWriter():
    """
    Fixture to create a FileWriter instance with a mock logger.
    
    Returns:
        FileWriter: An instance of FileWriter with a mocked logger.
    """
    logger = MagicMock()
    return FileWriter(logger)

@pytest.fixture
def tmpPath():
    """
    Fixture to create a temporary 'tmp' directory in the same folder as the test file.
    After the test finishes, it cleans up all files within the 'tmp' directory.

    Returns:
        str: The path to the temporary directory.
    """
    basePath = os.path.dirname(__file__)
    tmpPath = os.path.join(basePath, 'tmp')
    os.makedirs(tmpPath, exist_ok=True)

    # Provide tmpPath to the test
    yield tmpPath

    # Cleanup: remove all files in the tmp folder after the test completes
    for fileName in os.listdir(tmpPath):
        filePath = os.path.join(tmpPath, fileName)
        try:
            if os.path.isfile(filePath):
                os.remove(filePath)
        except Exception as e:
            print(f"Failed to delete {filePath}: {e}")

    # Optional: remove the tmp directory itself after all files are cleared
    try:
        os.rmdir(tmpPath)
    except OSError:
        # Directory is not empty or other error occurred, so we ignore
        pass

def testWriteProgramDataTruncatesLongTitle(fileWriter, tmpPath):
    """
    Validates that the title is truncated to 120 characters if it exceeds the limit.
    """
    tempFile = os.path.join(tmpPath, "testOutput.txt")

    program = {
        "date": "2025-02-28",
        "hour": "14:00",
        "title": "A" * 150,  # Title with 150 characters
        "content": "This is a sample description."
    }

    with open(tempFile, "w", encoding="utf-8") as file:
        currentDate = None
        currentDate = fileWriter.writeProgramData(file, program, currentDate)

    with open(tempFile, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Validate only one date line is written
    assert lines[0].strip() == "2025-02-28"

    # Validate that the title was truncated to 120 characters
    programLine = lines[1]
    parts = programLine.split("---")
    truncatedTitle = parts[1]

    assert len(truncatedTitle) == 120
    assert truncatedTitle == "A" * 120

def testWriteProgramDataWritesNormalTitle(fileWriter, tmpPath):
    """
    Validates normal behavior when the title is within 120 characters.
    """
    tempFile = os.path.join(tmpPath, "testOutputNormal.txt")

    program = {
        "date": "2025-02-28",
        "hour": "14:00",
        "title": "Short Title",
        "content": "This is a sample description."
    }

    with open(tempFile, "w", encoding="utf-8") as file:
        currentDate = None
        currentDate = fileWriter.writeProgramData(file, program, currentDate)

    with open(tempFile, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Validate date line
    assert lines[0].strip() == "2025-02-28"

    # Validate that the title was written correctly
    programLine = lines[1]
    parts = programLine.split("---")
    assert parts[1] == "Short Title"
