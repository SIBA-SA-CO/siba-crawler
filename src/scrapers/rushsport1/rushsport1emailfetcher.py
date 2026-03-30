import email
import fnmatch
import imaplib
import os
from email.header import decode_header

from src.scrapers.rushsport1.parserushsport1xlsx import parseRushSport1Xlsx


class RushSport1EmailFetcher:
    def __init__(self, logger):
        self.logger = logger
        self.subject_filter = "RUSH Schedule"
        self.subject_filters = ["RUSH Schedule"]
        self.file_extension = ".xlsx"
        self.filename_pattern = "rushprogramming schedule (rush sports 1)*"

        self.host = os.getenv("EMAIL_IMAP_HOST")
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")

    def fetchData(self) -> dict:
        self.logger.logInfo("Conectando a correo...")

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

                if not fnmatch.fnmatch(normalized_filename, self.filename_pattern):
                    continue

                file_content = part.get_payload(decode=True)
                return parseRushSport1Xlsx(file_content)

        self.logger.logCritical(
            f"No se encontró archivo '{self.filename_pattern}' con extensión '{self.file_extension}'."
        )
        return {}

    def _subject_matches(self, subject: str) -> bool:
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
