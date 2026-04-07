from datetime import datetime

from src.scrapers.core.interfaces.iurlformatter import IUrlFormatter


class RtpMundoUrlFormatter(IUrlFormatter):
    def formatUrl(self, targetDate: datetime, baseUrl: str) -> str:
        formattedDate = f"{targetDate.day}-{targetDate.strftime('%m-%Y')}"
        return f"{baseUrl}{formattedDate}"

