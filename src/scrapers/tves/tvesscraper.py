from src.scrapers.core.scraperbase import ScraperBase


class TvesScraper(ScraperBase):
    WEEKDAY_URLS = {
        0: "https://www.tves.gob.ve/programacion/",
        1: "https://www.tves.gob.ve/programacion-martes/",
        2: "https://www.tves.gob.ve/miercoles-programacion/",
        3: "https://www.tves.gob.ve/jueves-programacion/",
        4: "https://www.tves.gob.ve/viernes-programacion/",
        5: "https://www.tves.gob.ve/sabado-programacion/",
        6: "https://www.tves.gob.ve/domingo-programacion/",
    }

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict):
        defaultSynopsis = self.channelConfig["defaultDescription"]
        fileName = self.channelConfig["fileName"]
        filePath = self.channelConfig["outputPath"]
        rawPages = {}

        for weekday, url in self.WEEKDAY_URLS.items():
            pageContent = self.getDataFromUrl(url)
            if pageContent:
                rawPages[weekday] = pageContent

        self.dataProcessor.initialDate = startDate
        self.dataProcessor.daysRange = numberOfDays

        data = self.dataProcessor.processData(rawPages, defaultSynopsis, None)
        self.saveData(fileName, data, charReplacements, filePath)

