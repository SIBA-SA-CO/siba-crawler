import json
import pytz
import re
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor


class GameShowNetworkDataProcessor(IDataProcessor):
    """
    Processes Game Show Network schedule data from the JSON API response.

    The site now renders schedule cards client-side from a JSON endpoint, so this
    processor handles the API payload directly and keeps a lightweight HTML-string
    fallback for resilience.
    """

    def __init__(self, timezone: str):
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str) -> list:
        processedEvents = []
        scheduleItems = self._extractScheduleItems(rawData)

        for item in scheduleItems:
            startTime = item.get("STARTDATETIME")
            title = self._normalizeText(item.get("EPISODESERIESTITLE") or item.get("TAPE_TITLE") or "")
            if not startTime or not title:
                continue

            eventDateTime = self._parseSourceDatetime(startTime)
            if not eventDateTime:
                continue

            localizedEventDatetime = self.sourceTimezone.localize(eventDateTime)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

            hostName = self._formatHostName(item.get("EPISODEHOSTNAME", ""))
            description = self._normalizeText(
                item.get("EPISODE_DESCRIPTION")
                or item.get("EPISODEDESCRIPTION")
                or item.get("CONTRACT_DESCRIPTION")
                or ""
            )

            content = defaultDescription
            if hostName and description:
                content = f"Host: {hostName} - {description}"
            elif description:
                content = description
            elif hostName:
                content = f"Host: {hostName}"

            processedEvents.append({
                "date": targetEventDatetime.strftime("%Y-%m-%d"),
                "hour": targetEventDatetime.strftime("%H:%M"),
                "title": title,
                "content": content,
            })

        return sorted(processedEvents, key=lambda x: (x["date"], x["hour"]))

    def _extractScheduleItems(self, rawData) -> list:
        if isinstance(rawData, list):
            return rawData

        if isinstance(rawData, dict):
            if isinstance(rawData.get("items"), list):
                return rawData["items"]
            if isinstance(rawData.get("data"), list):
                return rawData["data"]
            return []

        if not isinstance(rawData, str):
            return []

        strippedData = rawData.strip()
        if strippedData.startswith("[") or strippedData.startswith("{"):
            try:
                parsedData = json.loads(strippedData)
                return self._extractScheduleItems(parsedData)
            except json.JSONDecodeError:
                pass

        return self._extractEmbeddedJson(strippedData)

    def _extractEmbeddedJson(self, html: str) -> list:
        endpointMatch = re.search(
            r'const\s+api_endpoint_url\s*=\s*"(?P<endpoint>https://[^"]+/get_show_schedule\.json)"',
            html
        )
        if not endpointMatch:
            return []

        return []

    def _parseSourceDatetime(self, value: str):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def _normalizeText(self, value: str) -> str:
        return re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()

    def _formatHostName(self, rawHostName: str) -> str:
        hostName = self._normalizeText(rawHostName)
        if "," not in hostName:
            return hostName

        nameParts = [part.strip() for part in hostName.split(",") if part.strip()]
        if len(nameParts) < 2:
            return hostName

        return f"{' '.join(nameParts[1:])} {nameParts[0]}".strip()
