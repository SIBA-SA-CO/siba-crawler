from datetime import date, datetime, time, timedelta

import pandas as pd
import pytz

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class RushSport1DataProcessor(IDataProcessor):
    def __init__(self, timezone: str):
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str) -> list:
        processedEvents = []

        for _, row in rawData.iterrows():
            try:
                eventDate = self._parse_date(row.get("Program Start Date"))
                eventTime = self._parse_time(row.get("Program Start Time"))
                eventTitle = self._normalize_text(row.get("Program Title"))
                eventContent = self._normalize_text(row.get("Program Description")) or defaultDescription

                if not eventDate or not eventTime or not eventTitle:
                    continue

                processedEvents.append(
                    self._build_event(eventDate, eventTime, eventTitle, eventContent)
                )

            except Exception as e:
                print(f"[Error] Evento con error: {e}")
                continue

        return processedEvents

    def _build_event(self, eventDate: date, eventTime: time, title: str, content: str) -> dict:
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
        for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        return None

    def _time_from_seconds(self, total_seconds: int) -> time:
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return time(hour=hours, minute=minutes)

    def _normalize_text(self, value) -> str:
        if pd.isna(value):
            return ""

        return str(value).strip()
