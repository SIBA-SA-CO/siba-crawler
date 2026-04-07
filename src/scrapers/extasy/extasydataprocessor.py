from datetime import datetime
from html import unescape

from bs4 import BeautifulSoup

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class ExtasyDataProcessor(IDataProcessor):
    def __init__(self, timezone: str):
        self.timezone = timezone

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        if not rawData:
            return []

        soup = BeautifulSoup(rawData, "html.parser")
        dayContainers = soup.select("div[id^='den']")
        if not dayContainers:
            return []

        processedEvents = []

        for dayContainer in dayContainers:
            headerElement = dayContainer.select_one("div.tvden")
            scheduleRows = dayContainer.select("div.tvblok > div.flex")

            if not headerElement or not scheduleRows:
                continue

            scheduleDate = self._parse_schedule_date(headerElement.get_text(" ", strip=True))
            if scheduleDate is None:
                continue

            for row in scheduleRows:
                timeElement = row.find("div")
                contentElement = row.select_one("div.w-full")

                if not timeElement or not contentElement:
                    continue

                eventTime = self._normalize_text(timeElement.get_text(" ", strip=True))
                eventTitle = self._normalize_text(contentElement.get_text(" ", strip=True))

                if not eventTime or not eventTitle:
                    continue

                processedEvents.append({
                    "date": scheduleDate.strftime("%Y-%m-%d"),
                    "hour": eventTime,
                    "title": eventTitle,
                    "content": defaultDescription,
                })

        return sorted(processedEvents, key=lambda item: (item["date"], item["hour"]))

    def _parse_schedule_date(self, headerText: str):
        match = None
        for token in headerText.split():
            if token.count(".") >= 2:
                match = token
                break

        if match is None:
            return None

        cleanedDate = match.strip(".")
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                return datetime.strptime(cleanedDate, fmt).date()
            except ValueError:
                continue

        return None

    def _normalize_text(self, value: str) -> str:
        return unescape(value or "").replace("\xa0", " ").strip()
