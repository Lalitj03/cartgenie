import pytest
from unittest.mock import patch, MagicMock

# Import the class from the module we intend to test
from core.db.neo4j_connector import Neo4jConnector

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Fixture to automatically mock environment variables for all tests in this file."""
    monkeypatch.setenv("NEO4J_URI", "bolt://mock_uri:7687")
    monkeypatch.setenv("NEO4J_USER", "mock_user")
    monkeypatch.setenv("NEO4J_PASSWORD", "mock_password")

@pytest.fixture
def clean_singleton():
    """Fixture to reset the singleton instance before each test."""
    # This ensures tests are isolated from each other
    if hasattr(Neo4jConnector, '_instance') and Neo4jConnector._instance is not None:
        Neo4jConnector._instance.close() # Close any open drivers
    Neo4jConnector._instance = None
    yield
    # Teardown
    if hasattr(Neo4jConnector, '_instance') and Neo4jConnector._instance is not None:
        # Check if _driver was initialized before trying to close
        if hasattr(Neo4jConnector._instance, '_driver'):
            Neo4jConnector._instance.close()
    Neo4jConnector._instance = None


def test_connector_is_a_singleton(clean_singleton):
    """
    Test Case: The connector correctly implements the singleton pattern.
    """
    instance1 = Neo4jConnector()
    instance2 = Neo4jConnector()
    assert instance1 is instance2

@patch('neo4j.GraphDatabase.driver')
def test_connection_is_established_on_first_query(mock_driver_factory, clean_singleton):
    """
    Test Case: The driver is created and verified only when a query is first executed.
    """
    # Arrange
    mock_driver = MagicMock()
    mock_driver_factory.return_value = mock_driver

    connector = Neo4jConnector()

    # Assert initial state
    mock_driver_factory.assert_not_called()
    assert connector._driver is None

    # Act
    with patch.object(mock_driver, 'session') as mock_session:
        mock_session.return_value.__enter__.return_value.run.return_value = []
        connector.execute_query("RETURN 1")

    # Assert connection was made
    mock_driver_factory.assert_called_once_with("bolt://mock_uri:7687", auth=("mock_user", "mock_password"))
    mock_driver.verify_connectivity.assert_called_once()

@patch('neo4j.GraphDatabase.driver')
def test_connection_is_closed_properly(mock_driver_factory, clean_singleton):
    """
    Test Case: The close method correctly closes an active driver.
    """
    # Arrange
    mock_driver = MagicMock()
    mock_driver.closed.return_value = False
    mock_driver_factory.return_value = mock_driver

    connector = Neo4jConnector()
    # Establish connection
    with patch.object(mock_driver, 'session') as mock_session:
        mock_session.return_value.__enter__.return_value.run.return_value = []
        connector.execute_query("RETURN 1")

    # Act
    connector.close()

    # Assert
    mock_driver.close.assert_called_once()

def test_init_raises_error_if_env_vars_missing(monkeypatch, clean_singleton):
    """
    Test Case: The connector raises a ValueError if config is missing.
    """
    # Arrange
    monkeypatch.delenv("NEO4J_URI")

    # Act & Assert
    with pytest.raises(ValueError, match="must be set in the environment"):
        Neo4jConnector()