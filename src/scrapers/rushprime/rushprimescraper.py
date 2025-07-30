from src.scrapers.core.scraperbase import ScraperBase

class RushPrimeScraper(ScraperBase):
    """
    Scraper especializado para el canal Rush Prime.

    Este scraper obtiene datos desde un adjunto de correo electrónico (CSV),
    los procesa con la clase `RushPrimeDataProcessor`, y finalmente guarda los eventos
    procesados en el formato estándar del sistema.

    Métodos:
        scrapeProgramGuide(startDate, numberOfDays, charReplacements):
            Ejecuta el flujo completo de obtención, procesamiento y guardado de datos.
    """

    def scrapeProgramGuide(self, startDate: str, numberOfDays: int, charReplacements: dict) -> None:
        """
        Ejecuta el proceso de scraping para Rush Prime.

        Obtiene los datos crudos desde la fuente (correo electrónico),
        los procesa usando `dataProcessor` y los guarda en un archivo.

        Args:
            startDate (str): Fecha inicial del scraping (no se usa directamente en este scraper).
            numberOfDays (int): Número de días a cubrir (no se usa directamente en este scraper).
            charReplacements (dict): Diccionario de reemplazos de caracteres para limpieza del contenido.
        """
        defaultSynopsis = self.channelConfig['defaultDescription']
        fileName = self.channelConfig['fileName']
        filePath = self.channelConfig['outputPath']

        # Obtener los datos desde la fuente (correo con adjunto CSV)
        rawData = self.dataFetcher.fetchData()

        # Verificar si se obtuvieron datos válidos
        if rawData is None or rawData.empty:
            return

        # Procesar los datos y guardar el resultado
        data = self.dataProcessor.processData(rawData, defaultSynopsis, targetDate='')
        self.saveData(fileName, data, charReplacements, filePath)
