import io
import email
import imaplib
import os
import re
import socket
import time
import zipfile
from contextlib import contextmanager
from email.header import decode_header
from fnmatch import fnmatch
from html import unescape
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from src.scrapers.core.interfaces.idatafetcher import IDataFetcher
from src.scrapers.cala.parsecalaxlsx import parseCalaXlsx


class CalaDropboxFetcher(IDataFetcher):
    """Descarga y extrae archivos Excel de la carpeta publica de Dropbox de CALA.

    Dropbox entrega las carpetas compartidas como un ZIP cuando se fuerza
    `dl=1`. Este fetcher descarga ese ZIP una sola vez por ejecucion, lo deja en
    memoria y luego busca dentro del archivo comprimido el Excel que corresponde
    al patron solicitado por cada subcanal.
    """

    def __init__(self, logger):
        """Inicializa el fetcher con limites conservadores de red.

        `_archive_content` funciona como cache local para evitar descargar el
        mismo ZIP varias veces cuando `CalaScraper` procesa varios subcanales.
        """
        self.logger = logger
        self.timeout = 60
        self.maxRetries = 3
        self._archive_content = None
        self._email_url = None
        self.subject_filter = "CalaTelevision"

        self.host = os.getenv("EMAIL_IMAP_HOST")
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")

    def fetchData(self, url: str, filename_pattern: str):
        """Retorna un DataFrame con el Excel que coincide con `filename_pattern`.

        Si no se puede descargar el ZIP, si Dropbox devuelve contenido invalido
        o si no existe ningun Excel compatible con el patron, se retorna `None`
        para que el scraper omita ese subcanal sin detener toda la ejecucion.
        """
        archive_content = self._get_archive_content(url)
        if archive_content is None:
            return None

        try:
            with zipfile.ZipFile(io.BytesIO(archive_content)) as archive:
                entry = self._find_entry(archive, filename_pattern)
                if entry is None:
                    self.logger.logCritical(
                        f"No se encontro archivo en Dropbox para el patron '{filename_pattern}'."
                    )
                    return None

                self.logger.logInfo(f"Procesando archivo CALA: {entry.filename}")
                return parseCalaXlsx(archive.read(entry))
        except zipfile.BadZipFile:
            self.logger.logError("Dropbox no retorno un ZIP valido para la carpeta de EPGs CALA.")
            return None

    def _get_archive_content(self, _url: str):
        """Descarga el ZIP de Dropbox con reintentos y cache en memoria."""
        if self._archive_content is not None:
            return self._archive_content

        source_url = self._resolve_source_url()
        if not source_url:
            self.logger.logCritical("No se encontro enlace de EPGs CALA en correo.")
            return None

        download_url = self._build_download_url(source_url)

        for attempt in range(1, self.maxRetries + 1):
            try:
                self.logger.logInfo(
                    f"Intento {attempt}/{self.maxRetries}: descargando EPGs CALA desde Dropbox: {download_url}"
                )
                with self._dropbox_dns_fallback():
                    response = requests.get(download_url, timeout=self.timeout)
                response.raise_for_status()
                self._archive_content = response.content
                return self._archive_content
            except requests.RequestException as request_error:
                self.logger.logError(
                    f"Error descargando EPGs CALA (Intento {attempt}/{self.maxRetries}): {request_error}"
                )
                if attempt < self.maxRetries:
                    time.sleep(attempt)

        return None

    def _resolve_source_url(self) -> str | None:
        """Obtiene el enlace mensual de EPGs desde correo."""
        if self._email_url:
            return self._email_url

        email_url = self._find_epg_url_in_email()
        if email_url:
            self._email_url = email_url
            return self._email_url

        return None

    def _find_epg_url_in_email(self) -> str | None:
        if not self.host or not self.username or not self.password:
            self.logger.logCritical(
                "Faltan variables de entorno de correo: EMAIL_IMAP_HOST, EMAIL_USERNAME o EMAIL_PASSWORD."
            )
            return None

        mail = None
        try:
            self.logger.logInfo("Buscando enlace CALA en correo...")
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.username, self.password)
            mail.select("inbox")

            result, data = mail.search(None, f'(SUBJECT "{self.subject_filter}")')
            if result != "OK" or not data or not data[0]:
                self.logger.logCritical(f"No se encontraron correos con asunto '{self.subject_filter}'.")
                return None

            mail_ids = sorted(set(data[0].split()), key=lambda value: int(value))
            for email_id in reversed(mail_ids):
                result, msg_data = mail.fetch(email_id, "(RFC822)")
                if result != "OK" or not msg_data:
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                decoded_subject = self._decode_header_value(msg.get("Subject", ""))
                if self.subject_filter.lower() not in decoded_subject.lower():
                    continue

                epg_url = self._extract_epg_url_from_message(msg)
                if epg_url:
                    self.logger.logInfo(f"Enlace EPGs CALA encontrado en correo: {epg_url}")
                    return epg_url
        except (imaplib.IMAP4.error, OSError, socket.gaierror) as mail_error:
            self.logger.logError(f"Error conectando al correo '{self.host}': {mail_error}")
            return None
        finally:
            if mail is not None:
                try:
                    mail.logout()
                except (imaplib.IMAP4.error, OSError):
                    pass

        self.logger.logCritical("No se encontro enlace de EPGs CALA en los correos.")
        return None

    def _extract_epg_url_from_message(self, msg) -> str | None:
        body = "\n".join(self._iter_text_parts(msg))
        if not body:
            return None

        body = unescape(body)
        urls = [
            url.rstrip(").,;")
            for url in re.findall(r"https?://[^\s<>\"']+", body)
        ]
        dropbox_urls = [url for url in urls if "dropbox.com" in url.lower()]

        for url in dropbox_urls:
            if "/epgs" in urlsplit(url).path.lower():
                return url

        return dropbox_urls[0] if dropbox_urls else None

    def _iter_text_parts(self, msg):
        parts = msg.walk() if msg.is_multipart() else [msg]

        for part in parts:
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition"):
                continue
            if part.get_content_type() not in {"text/plain", "text/html"}:
                continue

            payload = part.get_payload(decode=True)
            if payload is None:
                payload = part.get_payload()
                if isinstance(payload, str):
                    yield payload
                continue

            yield payload.decode(part.get_content_charset() or "utf-8", errors="replace")

    def _decode_header_value(self, value: str) -> str:
        decoded_parts = decode_header(value)
        decoded_value = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_value += part.decode(encoding or "utf-8", errors="replace")
            else:
                decoded_value += part

        return decoded_value

    @contextmanager
    def _dropbox_dns_fallback(self):
        """Resuelve hosts temporales de Dropbox con DNS alterno si falla el DNS local.

        Algunos enlaces publicos de Dropbox redirigen a subdominios dinamicos de
        `dl.dropboxusercontent.com`. En ciertos entornos esos hosts pueden fallar
        con `socket.gaierror`; durante la descarga se intercepta esa resolucion y
        se consulta Google DNS como respaldo. El `getaddrinfo` original siempre se
        restaura al salir del contexto.
        """
        original_getaddrinfo = socket.getaddrinfo

        def getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            try:
                return original_getaddrinfo(host, port, family, type, proto, flags)
            except socket.gaierror:
                if not str(host).endswith(".dl.dropboxusercontent.com"):
                    raise

                resolved_ip = self._resolve_dropbox_host(host)
                if not resolved_ip:
                    raise

                return [
                    (
                        socket.AF_INET,
                        type or socket.SOCK_STREAM,
                        proto or socket.IPPROTO_TCP,
                        "",
                        (resolved_ip, port),
                    )
                ]

        socket.getaddrinfo = getaddrinfo
        try:
            yield
        finally:
            socket.getaddrinfo = original_getaddrinfo

    def _resolve_dropbox_host(self, host: str) -> str | None:
        """Obtiene una direccion IPv4 para `host` usando DNS-over-HTTPS."""
        try:
            response = requests.get(
                "https://dns.google/resolve",
                params={"name": host, "type": "A"},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as request_error:
            self.logger.logError(f"No se pudo resolver DNS alterno para '{host}': {request_error}")
            return None

        for answer in response.json().get("Answer", []):
            ip_address = answer.get("data", "")
            if answer.get("type") == 1 and ip_address.count(".") == 3:
                return ip_address

        return None

    def _find_entry(self, archive: zipfile.ZipFile, filename_pattern: str):
        """Busca el Excel del subcanal dentro del ZIP.

        Primero intenta una coincidencia exacta con `fnmatch`. Si el nombre real
        del proveedor cambia levemente, usa una segunda estrategia mas tolerante:
        extrae las palabras significativas del patron y exige que todas aparezcan
        en el nombre del archivo. Se ignoran terminos genericos que no ayudan a
        distinguir canales.
        """
        normalized_pattern = filename_pattern.lower()
        required_words = [
            word
            for word in normalized_pattern.replace("*", " ").replace(".xlsx", " ").split()
            if word not in {"channel", "caribbean"}
        ]

        for entry in archive.infolist():
            if entry.is_dir():
                continue

            filename = entry.filename.rsplit("/", 1)[-1].lower()
            if not filename.endswith(".xlsx"):
                continue

            if fnmatch(filename, normalized_pattern):
                return entry

            if required_words and all(word in filename for word in required_words):
                return entry

        return None

    def _build_download_url(self, url: str) -> str:
        """Convierte un enlace compartido de Dropbox en URL de descarga directa."""
        parsed_url = urlsplit(url)
        query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
        query_params["dl"] = "1"
        query_params.pop("e", None)
        return urlunsplit(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                urlencode(query_params),
                "",
            )
        )
