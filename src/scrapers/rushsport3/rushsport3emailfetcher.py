from src.scrapers.core.emailattachmentdatafetcher import EmailAttachmentDataFetcher
from src.scrapers.rushsport3.parserushsport3xlsx import parseRushSport3Xlsx


class RushSport3EmailFetcher:
    def __init__(self, logger):
        self.fetcher = EmailAttachmentDataFetcher(
            logger=logger,
            subject_filter="EPG Schedule RushSports3",
            subject_filters=["RushSports3","EPG Schedule RushSports3", "RS3"],
            file_extension=".xlsx",
            filename_pattern="rs3 epg*.xlsx",
            parser=parseRushSport3Xlsx,
        )

    def fetchData(self) -> dict:
        return self.fetcher.fetchData()
