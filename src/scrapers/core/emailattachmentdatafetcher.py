# src/scrapers/core/emailattachmentdatafetcher.py

import email
import fnmatch
import imaplib
import os
import socket
from email.header import decode_header
from typing import Callable

from src.scrapers.core.interfaces.idatafetcher import IDataFetcher


class EmailAttachmentDataFetcher(IDataFetcher):
    """
    DataFetcher que obtiene datos desde un archivo adjunto de correo electronico,
    filtrando por asunto y por extension de archivo.
    """

    def __init__(
        self,
        logger,
        subject_filter: str,
        file_extension: str,
        parser: Callable[[bytes], dict],
        subject_filters: list[str] | None = None,
        filename_pattern: str | None = None
    ):
        self.logger = logger
        self.subject_filter = subject_filter
        self.subject_filters = [value for value in (subject_filters or [subject_filter]) if value]
        self.file_extension = file_extension.lower()
        self.parser = parser
        self.filename_pattern = filename_pattern.lower() if filename_pattern else None

        self.host = os.getenv("EMAIL_IMAP_HOST")
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")

    def fetchData(self) -> dict:
        self.logger.logInfo("Conectando a correo...")

        if not self.host or not self.username or not self.password:
            self.logger.logCritical(
                "Faltan variables de entorno de correo: EMAIL_IMAP_HOST, EMAIL_USERNAME o EMAIL_PASSWORD."
            )
            return None

        mail = None
        try:
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.username, self.password)
            mail.select("inbox")

            mail_ids = []
            for filter_value in self.subject_filters:
                result, data = mail.search(None, f'(SUBJECT "{filter_value}")')
                if result == "OK" and data and data[0]:
                    mail_ids.extend(data[0].split())

            mail_ids = sorted(set(mail_ids), key=lambda value: int(value))

            if not mail_ids:
                joined_filters = ", ".join(f"'{value}'" for value in self.subject_filters)
                self.logger.logCritical(f"No se encontraron correos con asunto {joined_filters}.")
                return {}

            for email_id in reversed(mail_ids):
                result, msg_data = mail.fetch(email_id, "(RFC822)")
                if result != "OK" or not msg_data:
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                decoded_subject = self._decode_header_value(msg.get("Subject", ""))

                if not self._subject_matches(decoded_subject):
                    continue

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = self._decode_header_value(part.get_filename() or "")
                    if not filename:
                        continue

                    normalized_filename = filename.lower()
                    if not normalized_filename.endswith(self.file_extension):
                        continue

                    if self.filename_pattern and not fnmatch.fnmatch(normalized_filename, self.filename_pattern):
                        continue

                    file_content = part.get_payload(decode=True)
                    print(part.get_filename())
                    return self.parser(file_content)
        except (imaplib.IMAP4.error, OSError, socket.gaierror) as mail_error:
            self.logger.logError(f"Error connecting to email server '{self.host}': {mail_error}")
            return None
        finally:
            if mail is not None:
                try:
                    mail.logout()
                except (imaplib.IMAP4.error, OSError):
                    pass

        if self.filename_pattern:
            self.logger.logCritical(
                f"No se encontro archivo '{self.filename_pattern}' con extension '{self.file_extension}'."
            )
            return {}

        self.logger.logCritical(f"No se encontro archivo con extension '{self.file_extension}'.")
        return {}

    def _subject_matches(self, subject: str) -> bool:
        if not subject:
            return True

        normalized_subject = subject.lower()
        return any(filter_value.lower() in normalized_subject for filter_value in self.subject_filters)

    def _decode_header_value(self, value: str) -> str:
        decoded_parts = decode_header(value)
        decoded_value = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_value += part.decode(encoding or "utf-8", errors="replace")
            else:
                decoded_value += part

        return decoded_value
