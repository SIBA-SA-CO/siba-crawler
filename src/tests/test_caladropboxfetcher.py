from email.message import EmailMessage
from unittest.mock import patch

from src.scrapers.cala.caladropboxfetcher import CalaDropboxFetcher


class DummyLogger:
    def logInfo(self, msg): pass
    def logCritical(self, msg): pass
    def logError(self, msg): pass


def test_extract_epg_url_prefers_epgs_over_schedules():
    fetcher = CalaDropboxFetcher(DummyLogger())
    msg = EmailMessage()
    msg.set_content(
        "Schedules: https://www.dropbox.com/scl/fo/current/Grids?rlkey=abc&dl=0\n"
        "EPG's: https://www.dropbox.com/scl/fo/current/EPGs?rlkey=abc&dl=0"
    )

    assert (
        fetcher._extract_epg_url_from_message(msg)
        == "https://www.dropbox.com/scl/fo/current/EPGs?rlkey=abc&dl=0"
    )


def test_resolve_source_url_does_not_use_configured_url_as_fallback():
    fetcher = CalaDropboxFetcher(DummyLogger())
    fetcher._find_epg_url_in_email = lambda: None

    assert fetcher._resolve_source_url() is None


@patch("src.scrapers.cala.caladropboxfetcher.imaplib.IMAP4_SSL")
def test_find_epg_url_in_latest_calatelevision_email(mock_imap, monkeypatch):
    monkeypatch.setenv("EMAIL_IMAP_HOST", "imap.test.com")
    monkeypatch.setenv("EMAIL_USERNAME", "user@test.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "secret")

    older_msg = EmailMessage()
    older_msg["Subject"] = "CalaTelevision previous"
    older_msg.set_content("EPGs: https://www.dropbox.com/scl/fo/older/EPGs?rlkey=old&dl=0")

    latest_msg = EmailMessage()
    latest_msg["Subject"] = "CalaTelevision current"
    latest_msg.set_content(
        "Schedules: https://www.dropbox.com/scl/fo/current/Grids?rlkey=new&dl=0\n"
        "EPGs: https://www.dropbox.com/scl/fo/current/EPGs?rlkey=new&dl=0"
    )

    instance = mock_imap.return_value
    instance.search.return_value = ("OK", [b"10 20"])
    instance.fetch.side_effect = [
        ("OK", [(None, latest_msg.as_bytes())]),
        ("OK", [(None, older_msg.as_bytes())]),
    ]

    fetcher = CalaDropboxFetcher(DummyLogger())

    assert fetcher._find_epg_url_in_email() == "https://www.dropbox.com/scl/fo/current/EPGs?rlkey=new&dl=0"
    instance.fetch.assert_called_once_with(b"20", "(RFC822)")
