"""
Zyte Web Scraping Client

This module provides a client for the Zyte API (formerly Scrapinghub), enabling
geolocation-aware web scraping for real-time product price data collection.
The client handles rate limiting, error handling, and response parsing.

Key Features:
- Geolocation-based scraping for region-specific content
- HTTP response body extraction
- Cookie handling for session management
- Comprehensive error handling and logging

Usage:
    client = ZyteClient()
    result = client.scrape_url("https://example.com/product", "IN")
    html_content = result.get("httpResponseBody")

Environment Variables Required:
- ZYTE_API_KEY: Authentication key for Zyte API access

The scraped content is then processed by Cognee for structured data extraction.
"""

import os
import requests
from dotenv import load_dotenv


class ZyteClient:
    """
    A client for interacting with the Zyte Web Scraping API.
    
    This client provides geolocation-aware web scraping capabilities,
    essential for getting region-specific pricing and product availability.
    Handles authentication, request formatting, and error management.
    
    Attributes:
        BASE_URL (str): Zyte API endpoint
        api_key (str): Authentication key loaded from environment
    """
    BASE_URL = "https://api.zyte.com/v1/extract"

    def __init__(self):
        """
        Initialize the Zyte client with API credentials.
        
        Loads the API key from environment variables and validates configuration.
        
        Raises:
            ValueError: If ZYTE_API_KEY environment variable is not set
        """
        load_dotenv()
        self.api_key = os.getenv("ZYTE_API_KEY")
        if not self.api_key:
            raise ValueError("ZYTE_API_KEY must be set in the environment.")

    def scrape_url(self, url: str, country_code: str) -> dict | None:
        """
        Scrapes a given URL using the Zyte API, with specific geolocation.

        This method performs geolocation-aware scraping to ensure region-specific
        content is retrieved. This is crucial for accurate pricing information
        as many e-commerce sites show different prices based on user location.

        Args:
            url (str): The target URL to scrape (product page, search results, etc.)
            country_code (str): The 2-letter ISO country code (e.g., "US", "IN", "GB")
                                for geolocation targeting
                                
        Returns:
            dict | None: Parsed JSON response from Zyte API containing:
                        - httpResponseBody: Raw HTML content
                        - responseCookies: Session cookies (if requested)
                        - Other metadata depending on request configuration
                        Returns None if the request fails
                        
        Raises:
            requests.RequestException: For network-related errors
        """
        # Configure scraping parameters
        payload = {
            "url": url,
            "httpResponseBody": True,  # Get the raw HTML content
            "geolocation": country_code.upper(),  # Target specific country
            "experimental": {
                "responseCookies": True  # Capture cookies for session handling
            }
        }
        
        try:
            # Make authenticated request to Zyte API
            response = requests.post(
                self.BASE_URL,
                auth=(self.api_key, ""),  # Zyte uses API key as username, empty password
                json=payload,
                timeout=30  # Set reasonable timeout for web scraping
            )
            
            # Handle successful responses
            if response.status_code == 200:
                return response.json()
            else:
                # Log detailed error information for debugging
                print(f"ERROR: Zyte API request failed for URL {url} with status {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            # Handle network errors, timeouts, etc.
            print(f"ERROR: Network error during Zyte API request for URL {url}: {e}")
            return None