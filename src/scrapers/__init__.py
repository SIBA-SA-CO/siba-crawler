import pkgutil
import inspect
import importlib
import src.scrapers  # Imports the root package
from src.scrapers.core.interfaces.ichannelscraper import IChannelScraper

def discoverScrapers():
    """
    Automatically detects all scraper classes within the `src.scrapers` package
    (including all subfolders), provided they inherit from `IChannelScraper`.

    This function searches the entire package and its submodules recursively,
    importing each module and inspecting its classes to find those that implement 
    the `IChannelScraper` interface.

    Returns:
        dict: A dictionary where the keys are the lowercase names of scraper classes 
              and the values are the scraper class objects.
    """
    scraperClasses = {}

    def findScrapersInModule(package):
        """
        Recursively searches for scrapers in all submodules of the provided package.

        Args:
            package (module): The package to search for scraper classes.
        """
        for _, moduleName, isPkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            # Dynamically import the module
            module = importlib.import_module(moduleName)

            # Inspect all the classes within the module
            for className, classObj in inspect.getmembers(module, inspect.isclass):
                # Check if the class is a subclass of IChannelScraper and belongs to the current module
                if issubclass(classObj, IChannelScraper) and classObj.__module__ == module.__name__:
                    scraperClasses[classObj.__name__.lower()] = classObj  # Store the scraper class in the dictionary

            # If it's a package, search within it recursively
            if isPkg:
                findScrapersInModule(module)

    # Start the search from the `src.scrapers` package
    findScrapersInModule(src.scrapers)

    return scraperClasses
