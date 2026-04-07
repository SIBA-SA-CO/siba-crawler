from src.scrapers.core.emailattachmentdatafetcher import EmailAttachmentDataFetcher
from src.scrapers.rushsport2.parserushsport2xlsx import parseRushSport2Xlsx


class RushSport2EmailFetcher:
    def __init__(self, logger):
        self.fetcher = EmailAttachmentDataFetcher(
            logger=logger,
            subject_filter="RUSHSPORTS2 Programming",
            subject_filters=["RUSHSPORTS2 Programming"],
            file_extension=".xlsx",
            filename_pattern="rushsports2 prgramming schedule*.xlsx",
            parser=parseRushSport2Xlsx,
        )

    def fetchData(self) -> dict:
        return self.fetcher.fetchData()

