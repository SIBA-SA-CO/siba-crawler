from datetime import date, datetime, time, timedelta

import pandas as pd
import pytz

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class CalaDataProcessor(IDataProcessor):
    """Normaliza la programacion CALA al formato comun usado por el sistema.

    El parser entrega un `DataFrame` con columnas tomadas de los Excel del
    proveedor. Este procesador valida fecha, hora y titulo; completa la sinopsis
    con la descripcion por defecto cuando hace falta; convierte la zona horaria
    de origen a America/Bogota; y elimina duplicados por fecha/hora.
    """

    def __init__(self, timezone: str):
        """Configura la zona horaria de origen indicada en `CHANNELS`."""
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str) -> list:
        """Convierte filas del Excel en eventos listos para `saveData`.

        `targetDate` no se usa porque CALA ya entrega varias fechas en la misma
        fuente. Las filas incompletas o con valores no parseables se descartan
        para evitar eventos corruptos en el archivo final.
        """
        processedEvents = []

        for _, row in rawData.iterrows():
            try:
                eventDate = self._parse_date(row.get("Date"))
                eventTime = self._parse_time(row.get("Start Time"))
                eventTitle = self._normalize_text(row.get("Title")) or self._normalize_text(row.get("Type"))
                eventContent = self._normalize_text(row.get("Description")) or defaultDescription

                if not eventDate or not eventTime or not eventTitle:
                    continue

                processedEvents.append(
                    self._build_event(eventDate, eventTime, eventTitle, eventContent)
                )

            except Exception as e:
                print(f"[Error] Evento con error: {e}")
                continue

        return self._sort_and_remove_duplicates(processedEvents)

    def _build_event(self, eventDate: date, eventTime: time, title: str, content: str) -> dict:
        """Construye un evento y convierte su fecha/hora a America/Bogota."""
        eventStartDatetime = datetime.combine(eventDate, eventTime)
        localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)
        targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

        return {
            "date": targetEventDatetime.strftime("%Y-%m-%d"),
            "hour": targetEventDatetime.strftime("%H:%M"),
            "title": title,
            "content": content,
        }

    def _parse_date(self, value):
        """Acepta fechas nativas de Excel, `datetime`, `date`, strings y valores pandas."""
        if pd.isna(value):
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            parsed_from_string = self._parse_date_string(value.strip())
            if parsed_from_string is not None:
                return parsed_from_string

        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None

        return parsed.date()

    def _parse_time(self, value):
        """Acepta horas nativas de Excel, fracciones de dia, `timedelta` y strings."""
        if pd.isna(value):
            return None

        if isinstance(value, datetime):
            return value.time().replace(second=0, microsecond=0)

        if isinstance(value, time):
            return value.replace(second=0, microsecond=0)

        if isinstance(value, timedelta):
            return self._time_from_seconds(int(value.total_seconds()))

        if isinstance(value, (int, float)) and 0 <= value < 1:
            total_seconds = int(round(value * 24 * 60 * 60))
            return self._time_from_seconds(total_seconds)

        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None

        return parsed.time().replace(second=0, microsecond=0)

    def _parse_date_string(self, value: str) -> date | None:
        """Prueba los formatos de fecha observados en los archivos CALA."""
        for fmt in ("%B %d %Y", "%b %d %Y", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        return None

    def _time_from_seconds(self, total_seconds: int) -> time:
        """Convierte segundos desde medianoche a `time`, normalizando sobre 24 horas."""
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return time(hour=hours, minute=minutes)

    def _normalize_text(self, value) -> str:
        """Limpia campos de texto y representa valores vacios como cadena vacia."""
        if pd.isna(value):
            return ""

        return str(value).strip()

    def _sort_and_remove_duplicates(self, events: list) -> list:
        """Ordena cronologicamente y conserva un solo evento por fecha/hora."""
        eventsByTime = {}

        for event in events:
            uniqueKey = (event["date"], event["hour"])
            eventsByTime[uniqueKey] = event

        return sorted(eventsByTime.values(), key=lambda item: (item["date"], item["hour"]))
