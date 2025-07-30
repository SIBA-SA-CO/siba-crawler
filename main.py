import argparse
import importlib
from datetime import datetime
from src.config import CHANNELS
from src.scrapers import discoverScrapers
from src.scrapers.core.logger import Logger
from dotenv import load_dotenv

def loadClassFromModulePath(classPath):
    """
    Loads a class from a string representing its full module path.

    Args:
        fullClassPath (str): The full path of the class, including the module and class name.

    Returns:
        type: The class object dynamically imported from the specified module.
    """
    moduleName, className = classPath.rsplit(".", 1)  # Split the module and class names
    module = importlib.import_module(moduleName)  # Import the module
    return getattr(module, className)  # Retrieve the class from the module

def runScraper(channel, initialDate, daysRange, characterReplacements):
    """
    Runs the scraper for a specific TV channel.

    Args:
        channel (str): The TV channel to scrape.
        initialDate (str): The start date for scraping in YYYY-MM-DD format.
        daysRange (int): The number of days to scrape before and after the initial date.
        characterReplacements (dict): Character replacements to apply in the data processing.

    Returns:
        None
    """
    availableScrapers = discoverScrapers()
    scraperClass = availableScrapers.get(channel)

    if not scraperClass:
        print(f"Warning: No scraper found for channel '{channel}'. Skipping...")
        return

    channelConfiguration = CHANNELS[channel]
    urlFormatterClass = loadClassFromModulePath(channelConfiguration["urlformatter"])
    dataFetcherClass = loadClassFromModulePath(channelConfiguration["datafetcher"])
    dataProcessorClass = loadClassFromModulePath(channelConfiguration["dataprocessor"])

    urlFormatterInstance = urlFormatterClass()
    dataFetcherInstance = dataFetcherClass(Logger())
    dataProcessorInstance = dataProcessorClass(channelConfiguration["timezone"])

    scraperInstance = scraperClass(
        channelConfiguration, 
        urlFormatterInstance,
        dataFetcherInstance, 
        dataProcessorInstance
    )

    scraperInstance.scrapeProgramGuide(initialDate, daysRange, characterReplacements)


def main():
    """
    Entry point for the TV program scraper.
    
    Parses command-line arguments, initializes the appropriate scraper for the selected TV channel,
    and executes the scraping process.
    """
    characterReplacements = {
        '&': 'en',
        "'": "’",
        "“": '"',
        " \r\n": " ",
        '\n': ' ',
        '': "’", 
        '': '-',  
        '': '"',  
        '': '"',
        "|": "-",
        ">":" ",
        "<":" "
        
    }

    load_dotenv()
    argumentParser = argparse.ArgumentParser(description="TV Program Guide Scraper")
    argumentParser.add_argument(
        "--initialDate", type=str, default=datetime.now().strftime("%Y-%m-%d"), 
        help="Start date for scraping in YYYY-MM-DD format"
    )
    argumentParser.add_argument(
        "--daysRange", type=int, default=15, 
        help="Number of days to scrape before and after the initial date"
    )
    argumentParser.add_argument(
        "--channel", type=str, choices=list(CHANNELS.keys()) + ["all"], required=True, 
        help=f"The TV channel to scrape. Options: {', '.join(CHANNELS.keys())}, or 'all' to scrape all channels."
    )
    
    parsedArguments = argumentParser.parse_args()

    if parsedArguments.channel == "all":
        for channel in CHANNELS.keys():
            runScraper(channel, parsedArguments.initialDate, parsedArguments.daysRange, characterReplacements)
    else:
        runScraper(parsedArguments.channel, parsedArguments.initialDate, parsedArguments.daysRange, characterReplacements)


if __name__ == "__main__":
    main()

