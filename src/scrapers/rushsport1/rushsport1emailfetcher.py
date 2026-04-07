from src.scrapers.core.emailattachmentdatafetcher import EmailAttachmentDataFetcher
from src.scrapers.rushsport1.parserushsport1xlsx import parseRushSport1Xlsx


class RushSport1EmailFetcher:
    def __init__(self, logger):
        self.fetcher = EmailAttachmentDataFetcher(
            logger=logger,
            subject_filter="RUSH Schedule",
            subject_filters=["RUSH Schedule"],
            file_extension=".xlsx",
            filename_pattern="rushprogramming schedule (rush sports 1)*",
            parser=parseRushSport1Xlsx,
        )

    def fetchData(self) -> dict:
        return self.fetcher.fetchData()
