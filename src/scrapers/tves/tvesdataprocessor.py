import re
from datetime import datetime, timedelta

import pytz
from bs4 import BeautifulSoup

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class TvesDataProcessor(IDataProcessor):
    TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}\s?(?:AM|PM)$", re.IGNORECASE)

    initialDate = None
    daysRange = None

    def __init__(self, timezone: str):
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: dict, defaultDescription: str, targetDate: str) -> list:
        if not rawData:
            return []

        scheduleTemplates = {
            weekday: self._extract_day_template(pageContent, defaultDescription)
            for weekday, pageContent in rawData.items()
        }

        initialDate = datetime.strptime(self.initialDate, "%Y-%m-%d")
        dateRange = [initialDate + timedelta(days=offset) for offset in range(-self.daysRange, self.daysRange + 1)]
        processedEvents = []

        for currentDate in dateRange:
            weekdayTemplate = scheduleTemplates.get(currentDate.weekday(), [])
            for item in weekdayTemplate:
                startTimeObj = datetime.strptime(
                    f"{currentDate.strftime('%Y-%m-%d')} {item['hour']}",
                    "%Y-%m-%d %H:%M"
                )
                localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

                processedEvents.append({
                    "date": targetEventDatetime.strftime("%Y-%m-%d"),
                    "hour": targetEventDatetime.strftime("%H:%M"),
                    "title": item["title"],
                    "content": item["content"],
                })

        return sorted(processedEvents, key=lambda item: (item["date"], item["hour"]))

    def _extract_day_template(self, rawPage: str, defaultDescription: str) -> list:
        soup = BeautifulSoup(rawPage, "html.parser")
        contentRoot = soup.select_one("div.entry-content")
        if contentRoot is None:
            contentRoot = soup

        textEditors = contentRoot.select("div.elementor-widget-text-editor div.elementor-widget-container")
        template = []
        pendingTime = None

        for editor in textEditors:
            text = self._normalize_text(editor.get_text(" ", strip=True))
            if not text:
                continue

            if self.TIME_PATTERN.match(text):
                pendingTime = datetime.strptime(text.upper(), "%I:%M %p").strftime("%H:%M")
                continue

            if pendingTime is None:
                continue

            template.append({
                "hour": pendingTime,
                "title": text,
                "content": defaultDescription,
            })
            pendingTime = None

        return template

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value or "").strip()

