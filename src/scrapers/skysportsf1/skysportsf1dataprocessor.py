import re
from datetime import datetime

import pytz
from bs4 import BeautifulSoup

from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class SkySportsF1DataProcessor(IDataProcessor):
    TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}\s(?:AM|PM)$", re.IGNORECASE)
    TITLE_LINK_PATTERN = re.compile(r"^\[(?P<title>[^\]]+)\]\((?P<url>https?://[^\)]+)\)$")
    IMAGE_LINK_PATTERN = re.compile(r"^\[!\[Image.*?\]\((?P<image>https?://[^\)]+)\)\]\((?P<url>https?://[^\)]+)\)$")
    NOISE_PATTERNS = (
        re.compile(r"^image", re.IGNORECASE),
        re.compile(r"^tvguide\.co\.uk", re.IGNORECASE),
        re.compile(r"^(sunday|monday|tuesday|wednesday|thursday|friday|saturday),?$", re.IGNORECASE),
        re.compile(r"^\d{1,2}\s+[A-Za-z]+$", re.IGNORECASE),
        re.compile(r"^channel numbers:?$", re.IGNORECASE),
        re.compile(r"^(bt tv|sky sports f1)$", re.IGNORECASE),
        re.compile(r"^\d{2,4}$"),
    )

    def __init__(self, timezone: str):
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData: str, defaultDescription: str, targetDate: str) -> list:
        htmlEvents = self._extractHtmlSchedule(rawData, defaultDescription)
        if htmlEvents:
            return sorted(htmlEvents, key=lambda item: (item["date"], item["hour"]))

        lines = self._extractContentLines(rawData)
        processedEvents = []
        index = 0

        while index < len(lines):
            currentLine = lines[index].strip()
            if not self.TIME_PATTERN.match(currentLine):
                index += 1
                continue

            showTime = currentLine
            index += 1
            block = []

            while index < len(lines) and not self.TIME_PATTERN.match(lines[index].strip()):
                strippedLine = lines[index].strip()
                if strippedLine:
                    block.append(strippedLine)
                index += 1

            program = self._parseProgramBlock(showTime, block, defaultDescription, targetDate)
            if program:
                processedEvents.append(program)

        return sorted(processedEvents, key=lambda item: (item["date"], item["hour"]))

    def _extractHtmlSchedule(self, rawData: str, defaultDescription: str) -> list:
        if "<html" not in rawData.lower() and "js-schedule" not in rawData.lower():
            return []

        soup = BeautifulSoup(rawData, "html.parser")
        scheduleItems = soup.select("div.js-schedule[data-date]")
        processedEvents = []

        for item in scheduleItems:
            rawDate = item.get("data-date", "").strip()
            titleElement = item.select_one("a.font-semibold")
            descriptionElement = item.select_one("div.hidden.md\\:block")
            fallbackDescriptionElement = item.select_one("div.md\\:hidden")

            if not rawDate or not titleElement:
                continue

            title = titleElement.get_text(" ", strip=True)
            description = ""

            if descriptionElement:
                description = descriptionElement.get_text(" ", strip=True)
            elif fallbackDescriptionElement:
                description = fallbackDescriptionElement.get_text(" ", strip=True)

            eventDate, eventTime = self._convertIsoDateTime(rawDate)
            content = description or defaultDescription

            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": content,
            })

        return processedEvents

    def _extractContentLines(self, rawData: str) -> list[str]:
        if "Markdown Content:" not in rawData:
            if "<html" in rawData.lower() or "<body" in rawData.lower():
                textContent = BeautifulSoup(rawData, "html.parser").get_text("\n")
                return textContent.splitlines()
            return rawData.splitlines()

        _, markdownContent = rawData.split("Markdown Content:", 1)
        return markdownContent.splitlines()

    def _parseProgramBlock(self, showTime: str, block: list[str], defaultDescription: str, targetDate: str):
        title = ""
        scheduleUrl = ""
        descriptions = []

        for line in block:
            titleMatch = self.TITLE_LINK_PATTERN.match(line)
            if titleMatch and not line.startswith("[![Image"):
                title = titleMatch.group("title").strip()
                scheduleUrl = titleMatch.group("url").strip()
                continue

            imageMatch = self.IMAGE_LINK_PATTERN.match(line)
            if imageMatch:
                scheduleUrl = scheduleUrl or imageMatch.group("url").strip()
                continue

            if self._isNoise(line):
                continue

            descriptions.append(line)

        if not title and scheduleUrl:
            title = self._titleFromScheduleUrl(scheduleUrl)

        if not title and descriptions:
            title = descriptions.pop(0)

        if not title:
            return None

        content = self._buildContent(descriptions, defaultDescription)
        eventDate, eventTime = self._convertDateTime(targetDate, showTime)

        return {
            "date": eventDate,
            "hour": eventTime,
            "title": title,
            "content": content,
        }

    def _buildContent(self, descriptions: list[str], defaultDescription: str) -> str:
        normalizedDescriptions = []

        for description in descriptions:
            if description not in normalizedDescriptions:
                normalizedDescriptions.append(description)

        if not normalizedDescriptions:
            return defaultDescription

        if len(normalizedDescriptions) == 1:
            return normalizedDescriptions[0]

        return " - ".join(normalizedDescriptions)

    def _convertDateTime(self, targetDate: str, showTime: str) -> tuple[str, str]:
        startTimeObj = datetime.strptime(f"{targetDate} {showTime.upper()}", "%Y-%m-%d %I:%M %p")
        localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
        targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
        return (
            targetEventDatetime.strftime("%Y-%m-%d").strip(),
            targetEventDatetime.strftime("%H:%M").strip(),
        )

    def _convertIsoDateTime(self, rawDate: str) -> tuple[str, str]:
        startTimeObj = datetime.fromisoformat(rawDate.replace("Z", "+00:00")).replace(tzinfo=None)
        localizedEventDatetime = self.sourceTimezone.localize(startTimeObj)
        targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
        return (
            targetEventDatetime.strftime("%Y-%m-%d").strip(),
            targetEventDatetime.strftime("%H:%M").strip(),
        )

    def _titleFromScheduleUrl(self, scheduleUrl: str) -> str:
        slug = scheduleUrl.rstrip("/").split("/")[-1]
        parts = [part for part in slug.split("-") if part]
        return " ".join(part.upper() if part.lower() == "f1" else part.capitalize() for part in parts)

    def _isNoise(self, line: str) -> bool:
        normalizedLine = line.strip()
        if not normalizedLine:
            return True

        return any(pattern.match(normalizedLine) for pattern in self.NOISE_PATTERNS)
