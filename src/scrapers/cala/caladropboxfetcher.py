import io
import socket
import time
import zipfile
from contextlib import contextmanager
from fnmatch import fnmatch
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

    def _get_archive_content(self, url: str):
        """Descarga el ZIP de Dropbox con reintentos y cache en memoria."""
        if self._archive_content is not None:
            return self._archive_content

        download_url = self._build_download_url(url)

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
