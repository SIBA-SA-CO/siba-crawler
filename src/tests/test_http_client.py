import pytest
import requests
from unittest.mock import MagicMock, patch
from src.scrapers.core.httpclient import HttpClient

@pytest.fixture
def mockLogger():
    """
    Creates a mock logger with logInfo and logError methods.
    """
    logger = MagicMock()
    logger.logInfo = MagicMock()
    logger.logError = MagicMock()
    return logger

@patch("requests.get")
def test_fetchData_json(mockGet, mockLogger):
    """
    Tests fetchData method when the response contains JSON data.
    """
    url = "https://example.com/data"
    expectedResponse = {"key": "value"}
    
    mockResponse = MagicMock()
    mockResponse.json.return_value = expectedResponse
    mockResponse.text = "{\"key\": \"value\"}"
    mockResponse.headers = {"Content-Type": "application/json"}
    mockResponse.raise_for_status = MagicMock()
    mockGet.return_value = mockResponse
    
    httpClient = HttpClient(mockLogger)
    result = httpClient.fetchData(url)

    assert result == expectedResponse
    mockLogger.logInfo.assert_called_with(f"Successfully retrieved data from {url}")

@patch("requests.get")
def test_fetchData_text(mockGet, mockLogger):
    """
    Tests fetchData method when the response contains plain text data.
    """
    url = "https://example.com/text"
    expectedResponse = "Sample text response"
    
    mockResponse = MagicMock()
    mockResponse.json.side_effect = ValueError("No JSON")
    mockResponse.text = expectedResponse
    mockResponse.headers = {"Content-Type": "text/plain"}
    mockResponse.raise_for_status = MagicMock()
    mockGet.return_value = mockResponse
    
    httpClient = HttpClient(mockLogger)
    result = httpClient.fetchData(url)
    
    assert result == expectedResponse
    mockLogger.logInfo.assert_called_with(f"Successfully retrieved data from {url}")

@patch("requests.get")
def test_fetchData_requestError(mockGet, mockLogger):
    """
    Tests fetchData method when an HTTP request error occurs.
    """
    url = "https://example.com/error"
    mockGet.side_effect = requests.RequestException("Request failed")
    
    httpClient = HttpClient(mockLogger)
    result = httpClient.fetchData(url)
    
    assert result is None
    mockLogger.logError.assert_called_with(f"Error retrieving data from {url}: Request failed")
