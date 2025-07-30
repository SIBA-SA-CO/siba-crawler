# src/scrapers/core/emailattachmentdatafetcher.py

import imaplib
import email
import os
from email.header import decode_header
from typing import Callable
from src.scrapers.core.interfaces.idatafetcher import IDataFetcher


class EmailAttachmentDataFetcher(IDataFetcher):
    """
    DataFetcher que obtiene datos desde un archivo adjunto de correo electrónico,
    filtrando por el asunto del correo y la extensión del archivo.

    Este fetcher permite inyectar una función parser para interpretar el contenido
    del adjunto en diferentes formatos como CSV, XLSX, JSON, etc.

    Atributos:
        logger: Logger utilizado para registrar mensajes del proceso.
        subject_filter (str): Texto parcial o completo del asunto del correo a buscar.
        file_extension (str): Extensión esperada del archivo adjunto (por ejemplo, ".csv", ".xlsx").
        parser (Callable[[bytes], dict]): Función que procesa el contenido binario del archivo adjunto.
        host (str): Servidor IMAP del proveedor de correo (obtenido desde variables de entorno).
        username (str): Usuario del correo electrónico (desde .env).
        password (str): Contraseña del correo electrónico (desde .env).
    """

    def __init__(
        self,
        logger,
        subject_filter: str,
        file_extension: str,
        parser: Callable[[bytes], dict]
    ):
        """
        Inicializa el EmailAttachmentDataFetcher.

        Args:
            logger: Instancia de logger para el seguimiento del proceso.
            subject_filter (str): Palabra o frase a buscar en el asunto del correo.
            file_extension (str): Extensión del archivo adjunto a buscar (ej: '.csv').
            parser (Callable): Función que toma el contenido del archivo en bytes y retorna un dict/dataframe.
        """
        self.logger = logger
        self.subject_filter = subject_filter
        self.file_extension = file_extension.lower()
        self.parser = parser
        
        self.host = os.getenv("EMAIL_IMAP_HOST")
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")

    def fetchData(self) -> dict:
        """
        Busca el correo más reciente que coincida con el filtro de asunto,
        extrae el archivo adjunto con la extensión especificada y lo procesa
        con el parser inyectado.

        Returns:
            dict: Datos procesados desde el archivo adjunto.
                  Si no se encuentra el correo o el adjunto esperado, se retorna un diccionario vacío.
        """
        self.logger.logInfo("Conectando a correo...")

        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.username, self.password)
        mail.select("inbox")

        result, data = mail.search(None, f'(SUBJECT "{self.subject_filter}")')
        mail_ids = data[0].split()

        if not mail_ids:
            self.logger.logCritical(f"No se encontraron correos con asunto '{self.subject_filter}'.")
            return {}

        latest_email_id = mail_ids[-1]
        result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename and filename.lower().endswith(self.file_extension):
                file_content = part.get_payload(decode=True)
                return self.parser(file_content)

        self.logger.logCritical(f"No se encontró archivo con extensión '{self.file_extension}'.")
        return {}
