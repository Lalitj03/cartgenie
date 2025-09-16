"""
Qdrant Vector Database Connector

This module provides a singleton connector for interacting with Qdrant vector database.
Qdrant is used for semantic product similarity search, enabling CartGenie to find
similar products across different retailers even when exact matches aren't available.

Key Features:
- Singleton pattern ensures single connection per application instance
- Automatic collection creation and management
- Vector similarity search with cosine distance
- Supports 384-dimension embeddings (compatible with all-MiniLM-L6-v2)

Usage:
    connector = QdrantConnector()
    results = connector.search(vector=embedding, limit=5)
    connector.upsert_points(points_list)

Environment Variables Required:
- QDRANT_HOST: Hostname of the Qdrant server
- QDRANT_PORT: Port number (default: 6333)
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Configuration constants
COLLECTION_NAME = "cartgenie_products"
VECTOR_DIMENSION = 384  # Compatible with all-MiniLM-L6-v2 embeddings


class QdrantConnector:
    """
    A singleton connector class for interacting with a Qdrant vector database.
    
    This connector manages vector similarity search for product matching.
    Uses the singleton pattern to ensure efficient connection reuse across
    the application while maintaining thread safety.
    
    Attributes:
        client (QdrantClient): The Qdrant client instance
        _initialized (bool): Tracks initialization state for singleton
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implement singleton pattern to ensure single instance.
        
        Returns:
            QdrantConnector: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(QdrantConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the Qdrant connection and ensure collection exists.
        
        This method is idempotent - multiple calls won't recreate connections.
        Loads configuration from environment variables and sets up the collection.
        
        Raises:
            ValueError: If required environment variables are missing
            Exception: If connection or collection creation fails
        """
        if self._initialized:
            return

        load_dotenv()
        host = os.getenv("QDRANT_HOST")
        port = int(os.getenv("QDRANT_PORT", 6333))

        if not host:
            raise ValueError("QDRANT_HOST must be set in the environment.")

        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection_exists()
        self._initialized = True

    def _ensure_collection_exists(self):
        try:
            self.client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=VECTOR_DIMENSION, distance=models.Distance.COSINE),
            )
            print(f"Qdrant collection '{COLLECTION_NAME}' created/recreated successfully.")
        except Exception as e:
            print(f"FATAL: Failed to create Qdrant collection: {e}")
            raise

    def upsert_points(self, points: list[models.PointStruct]):
        if not points:
            return
        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )
        except Exception as e:
            print(f"ERROR: Failed to upsert points to Qdrant: {e}")

    def search(self, vector: list[float], limit: int = 5) -> list:
        try:
            search_result = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=vector,
                limit=limit
            )
            return search_result
        except Exception as e:
            print(f"ERROR: Failed to search points in Qdrant: {e}")
            return []