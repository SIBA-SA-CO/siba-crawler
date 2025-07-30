# src/scrapers/rushprime/rushprime_email_fetcher_wrapper.py

from src.scrapers.core.emailattachmentdatafetcher import EmailAttachmentDataFetcher
from src.scrapers.rushprime.parserushprimecsv import parseRushPrimeCsv

class RushPrimeEmailFetcher:
    """
    Envoltorio especializado para obtener archivos adjuntos del correo electrónico con la programación de Rush Prime.

    Esta clase configura un `EmailAttachmentDataFetcher` con filtros específicos para correos que contienen
    archivos CSV de Rush Prime. Utiliza un parser personalizado para convertir el contenido del archivo
    en una estructura de datos utilizable (normalmente un DataFrame).

    Atributos:
        fetcher (EmailAttachmentDataFetcher): Instancia configurada para buscar archivos .csv con asunto "RUSH PRIME".
    """

    def __init__(self, logger):
        """
        Inicializa el fetcher con los parámetros específicos para Rush Prime.

        Args:
            logger: Instancia de logger que será utilizada para registrar mensajes durante la ejecución.
        """
        self.fetcher = EmailAttachmentDataFetcher(
            logger=logger,
            subject_filter="RUSH PRIME",
            file_extension=".csv",
            parser=parseRushPrimeCsv
        )

    def fetchData(self) -> dict:
        """
        Ejecuta la búsqueda y procesamiento del archivo adjunto desde el correo.

        Returns:
            dict: Estructura de datos procesada por el parser, generalmente un DataFrame.
                  Si no se encuentra un archivo o hay un error, retorna None o estructura vacía.
        """
        return self.fetcher.fetchData()
