import pytest
from unittest.mock import patch, MagicMock

# The module to be created
from core.utils.zyte_client import ZyteClient

@pytest.fixture
def mock_env_key(monkeypatch):
    """Mocks the ZYTE_API_KEY environment variable."""
    monkeypatch.setenv("ZYTE_API_KEY", "test_api_key")

def test_init_raises_error_if_api_key_is_missing(monkeypatch):
    """
    Test Case: The client raises a ValueError if the ZYTE_API_KEY is not set.
    """
    monkeypatch.delenv("ZYTE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ZYTE_API_KEY must be set"):
        ZyteClient()

def test_init_loads_api_key_from_env(mock_env_key):
    """
    Test Case: The client correctly loads the API key from environment variables.
    """
    client = ZyteClient()
    assert client.api_key == "test_api_key"

@patch('requests.post')
def test_scrape_url_sends_correct_request_payload(mock_post, mock_env_key):
    """
    Test Case: The scrape_url method sends a correctly formatted POST request
    to the Zyte API, including geolocation.
    """
    # Arrange
    client = ZyteClient()
    target_url = "https://example.com/product/123"
    target_country = "IN"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"httpResponseBody": "PGh0bWw+..."}
    mock_post.return_value = mock_response

    # Act
    result = client.scrape_url(target_url, country_code=target_country)

    # Assert
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args

    assert args[0] == "https://api.zyte.com/v1/extract"
    assert kwargs['auth'] == ("test_api_key", "")

    json_payload = kwargs['json']
    assert json_payload['url'] == target_url
    assert json_payload['geolocation'] == "IN"
    assert json_payload['httpResponseBody'] is True

    assert result == {"httpResponseBody": "PGh0bWw+..."}

@patch('requests.post')
def test_scrape_url_handles_api_error(mock_post, mock_env_key):
    """
    Test Case: The client returns None if the API call is not successful.
    """
    # Arrange
    client = ZyteClient()
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Authentication failed"
    mock_post.return_value = mock_response

    # Act
    result = client.scrape_url("https://example.com", "US")

    # Assert
    assert result is None