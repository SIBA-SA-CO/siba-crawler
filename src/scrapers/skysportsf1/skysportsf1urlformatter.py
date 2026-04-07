from datetime import datetime

from src.scrapers.core.interfaces.iurlformatter import IUrlFormatter


class SkySportsF1UrlFormatter(IUrlFormatter):
    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        return f"{baseUrl}{targetDate.strftime('%Y-%m-%d')}"

