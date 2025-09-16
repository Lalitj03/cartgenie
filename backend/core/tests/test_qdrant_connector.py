import pytest
from unittest.mock import patch, MagicMock
from qdrant_client import models

# Import the class from the module we intend to test
from core.db.qdrant_connector import QdrantConnector, COLLECTION_NAME

# This fixture will run for all tests in this file
@pytest.fixture(autouse=True)
def mock_connector_init():
    """
    Mocks the __init__ of the QdrantConnector to prevent it from running
    its own initialization logic (like creating a real client) during tests.
    We will manually set the 'client' attribute with a mock.
    """
    with patch.object(QdrantConnector, '__init__', return_value=None) as mock_init:
        yield mock_init

@pytest.fixture
def connector_with_mock_client():
    """
    Provides a QdrantConnector instance with a mocked internal client,
    ready for method testing.
    """
    # Reset the singleton for test isolation
    QdrantConnector._instance = None
    connector = QdrantConnector()
    connector.client = MagicMock() # Manually attach a mock client
    return connector

def test_connector_is_a_singleton():
    """
    Test Case: The connector correctly implements the singleton pattern.
    We test the __new__ method's logic directly.
    """
    QdrantConnector._instance = None # Ensure clean state
    instance1 = QdrantConnector()
    instance2 = QdrantConnector()
    assert instance1 is instance2

def test_upsert_points_calls_client_upsert(connector_with_mock_client):
    """
    Test Case: The upsert_points method correctly calls the client's upsert method.
    """
    test_points = [MagicMock()]

    # Act
    connector_with_mock_client.upsert_points(test_points)

    # Assert
    connector_with_mock_client.client.upsert.assert_called_once_with(
        collection_name=COLLECTION_NAME,
        points=test_points,
        wait=True
    )

def test_search_points_calls_client_search(connector_with_mock_client):
    """
    Test Case: The search method correctly calls the client's search method.
    """
    test_vector = [0.1, 0.2, 0.3, 0.4]
    test_limit = 5

    # Act
    connector_with_mock_client.search(vector=test_vector, limit=test_limit)

    # Assert
    connector_with_mock_client.client.search.assert_called_once_with(
        collection_name=COLLECTION_NAME,
        query_vector=test_vector,
        limit=test_limit
    )