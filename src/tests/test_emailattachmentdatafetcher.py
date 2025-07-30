import pytest
from unittest.mock import patch, MagicMock
from src.scrapers.core.emailattachmentdatafetcher import EmailAttachmentDataFetcher

@pytest.fixture
def dummy_logger():
    class DummyLogger:
        def logInfo(self, msg): pass
        def logCritical(self, msg): pass
    return DummyLogger()

@pytest.fixture
def fake_parser():
    def parser_fn(file_bytes):
        return {"parsed": True}
    return parser_fn

@patch("src.scrapers.core.emailattachmentdatafetcher.imaplib.IMAP4_SSL")
def test_fetch_data_success(mock_imap, dummy_logger, fake_parser, monkeypatch):
    # Simula variables de entorno
    monkeypatch.setenv("EMAIL_IMAP_HOST", "imap.test.com")
    monkeypatch.setenv("EMAIL_USERNAME", "user@test.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "secret")

    # Mocks de IMAP
    instance = mock_imap.return_value
    instance.login.return_value = "OK"
    instance.select.return_value = ("OK", [b""])
    instance.search.return_value = ("OK", [b"123"])
    instance.fetch.return_value = ("OK", [(None, b"raw email")])

    # Email simulado con archivo adjunto
    import email
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content("This is a test")
    msg.add_attachment(
        b"csv,data",
        maintype="text",
        subtype="csv",
        filename="file.csv"
    )
    instance.fetch.return_value = ("OK", [(None, msg.as_bytes())])

    fetcher = EmailAttachmentDataFetcher(
        logger=dummy_logger,
        subject_filter="RUSH PRIME",
        file_extension=".csv",
        parser=fake_parser
    )

    result = fetcher.fetchData()
    assert result == {"parsed": True}
