from datetime import datetime
from html import unescape

import pytz

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class RtpMundoDataProcessor(IDataProcessor):
    def __init__(self, timezone: str):
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str) -> list:
        processedEvents = []

        if not rawData or "result" not in rawData:
            return processedEvents

        for periodEvents in rawData["result"].values():
            if not isinstance(periodEvents, list):
                continue

            for event in periodEvents:
                rawDate = event.get("date")
                title = self._cleanText(event.get("name"))

                if not rawDate or not title:
                    continue

                eventStartDatetime = datetime.strptime(rawDate, "%Y-%m-%d %H:%M:%S")
                localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

                eventDate = targetEventDatetime.strftime("%Y-%m-%d")
                eventTime = targetEventDatetime.strftime("%H:%M")
                content = self._buildContent(event, defaultDescription)

                if targetDate and eventDate != targetDate:
                    continue

                processedEvents.append({
                    "date": eventDate,
                    "hour": eventTime,
                    "title": title,
                    "content": content,
                })

        return sorted(
            processedEvents,
            key=lambda item: (
                datetime.strptime(item["date"], "%Y-%m-%d"),
                datetime.strptime(item["hour"], "%H:%M")
            )
        )

    def _buildContent(self, event: dict, defaultDescription: str) -> str:
        description = self._cleanText(event.get("description"))
        episode = event.get("episode") or {}
        episodeTitle = self._cleanText(episode.get("title"))
        episodeSynopsis = self._cleanText(episode.get("sinopse"))

        contentParts = [value for value in (episodeTitle, description or episodeSynopsis) if value]
        if contentParts:
            return " - ".join(contentParts)

        return defaultDescription

    def _cleanText(self, value) -> str:
        if not value:
            return ""

        return unescape(str(value)).strip()

