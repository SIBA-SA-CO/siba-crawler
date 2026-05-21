from src.scrapers.core.scraperbase import ScraperBase


class CalaScraper(ScraperBase):
    """Orquesta la generacion de grillas EPG para los subcanales CALA.

    A diferencia de scrapers que producen un unico archivo de salida, CALA
    entrega varios canales dentro de una misma carpeta/ZIP de Dropbox. Por eso
    este scraper recorre la lista `subChannels` de la configuracion y ejecuta
    el mismo flujo de descarga, procesamiento y guardado para cada patron de
    archivo configurado.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict) -> None:
        """Descarga, procesa y guarda la programacion de cada subcanal CALA.

        `startDate` y `numberOfDays` se conservan en la firma por compatibilidad
        con `ScraperBase`, pero el proveedor CALA ya entrega el rango de fechas
        en los archivos Excel. El filtrado por fecha no se aplica aqui.
        """
        filePath = self.channelConfig["outputPath"]

        for subChannel in self.channelConfig["subChannels"]:
            # Cada subcanal apunta a un Excel distinto dentro del ZIP compartido.
            defaultSynopsis = subChannel["defaultDescription"]
            fileName = subChannel["fileName"]
            filenamePattern = subChannel["filenamePattern"]

            rawData = self.dataFetcher.fetchData(self.channelConfig["url"], filenamePattern)

            if rawData is None or rawData.empty:
                continue

            data = self.dataProcessor.processData(rawData, defaultSynopsis, targetDate="")
            self.saveData(fileName, data, charReplacements, filePath)
