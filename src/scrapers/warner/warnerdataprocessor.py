import pytz
import re
import defusedxml.ElementTree as ET
from defusedxml.ElementTree import parse
from datetime import datetime, timedelta, timezone
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class WarnerDataProcessor(IDataProcessor):

    def __init__(self, timezone: str):

        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription, targetDate):

        processedEvents = []
        
        root = ET.fromstring(rawData) 
        events = root[1].findall('Schedule')
        for event in events:
            title = ""
            content = defaultDescription
            gmt = event.find('gmt').text
            parseDate = datetime.strptime(gmt, "%a %b %d %H:%M:%S GMT %Y")
            localizedEventDatetime = self.sourceTimezone.localize(parseDate)
            targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)
            eventDate = targetEventDatetime.strftime("%Y-%m-%d").strip()
            eventTime = targetEventDatetime.strftime("%H:%M").strip()
            show = event.find('show')
            episode = show.find('episode')
            programTitle = show.find('programTitle').text
            episodeTitle = episode.find('episodeTitle').text
            description = episode.find('description').text

            if(programTitle and episodeTitle):
                title = f"{programTitle} - {episodeTitle}"
            else:
                title = programTitle

            if(description):
                content = description
                
            processedEvents.append({
                "date": eventDate,
                "hour": eventTime,
                "title": title,
                "content": content,
            })

        return processedEvents
