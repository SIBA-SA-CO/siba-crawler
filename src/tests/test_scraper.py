import os
import pytest
from src.config import CHANNELS
from main import runScraper
from datetime import datetime

def clearOutputFiles():
    """
    Deletes output files before running tests.
    """
    for channel in CHANNELS.values():
        if "subChannels" in channel:
            outputDir = channel["outputPath"]
            for subChannel in channel["subChannels"]:
                fileName = subChannel["fileName"]
                filePath = os.path.join(outputDir, f"{fileName}.txt")
                if os.path.exists(filePath):
                    os.remove(filePath)
        else:
            outputDir = channel["outputPath"]
            fileName = channel["fileName"]
            filePath = os.path.join(outputDir, f"{fileName}.txt")
            if os.path.exists(filePath):
                os.remove(filePath)

def testScraperOutput():
    """
    Runs each scraper with daysRange=0 and verifies that the output files are not empty.
    """
    clearOutputFiles()
    
    initialDate = datetime.now().strftime("%Y-%m-%d")  
    daysRange = 0
    characterReplacements = {
        '&': 'en', "'": "’", "“": '"', " \r\n": " ", '\n': ' ',
        '': "’", '': '-', '': '"', '': '"', "|": "-"
    }
    
    for channelName, channel in CHANNELS.items():
        if "subChannels" in channel:
            outputDir = channel["outputPath"]
            for subChannel in channel["subChannels"]:
                runScraper(channelName, initialDate, daysRange, characterReplacements)
                
                fileName = subChannel["fileName"]
                filePath = os.path.join(outputDir, f"{fileName}.txt")
                
                assert os.path.exists(filePath), f"The file {filePath} was not generated."
                assert os.path.getsize(filePath) > 0, f"The file {filePath} is empty."
        else:
            runScraper(channelName, initialDate, daysRange, characterReplacements)
            
            outputDir = channel["outputPath"]
            fileName = channel["fileName"]
            filePath = os.path.join(outputDir, f"{fileName}.txt")
            
            assert os.path.exists(filePath), f"The file {filePath} was not generated."
            assert os.path.getsize(filePath) > 0, f"The file {filePath} is empty."

if __name__ == "__main__":
    pytest.main(["-v", __file__])
