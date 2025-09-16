import os
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

class Neo4jConnector:
    """A singleton connector class for interacting with a Neo4j database."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Neo4jConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in the environment.")

        self._uri = uri
        self._user = user
        self._password = password
        self._driver: Driver | None = None
        self._initialized = True

    def _ensure_driver(self):
        if self._driver is None or self._driver.closed():
            try:
                self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
                self._driver.verify_connectivity()
            except Exception as e:
                print(f"FATAL: Failed to create or verify Neo4j driver: {e}")
                raise

    def close(self):
        if self._driver is not None and not self._driver.closed():
            self._driver.close()

    def execute_query(self, query: str, parameters: dict | None = None) -> list[dict]:
        self._ensure_driver()
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            print(f"ERROR: Failed to execute Neo4j query: {e}")
            return []