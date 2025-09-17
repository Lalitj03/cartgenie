"""
CartGenie AI Agent Tools

This module provides tools for CrewAI agents to interact with external systems:
- Vector database search for product similarity matching
- Web scraping for real-time price data
- Knowledge graph queries for historical price information

The tools integrate with sponsor technologies:
- Superlinked: For generating product embeddings (placeholder implementation)
- Cognee: For extracting structured product data from HTML (placeholder implementation)
- Zyte: For geolocation-aware web scraping
"""

from qdrant_client import models
import uuid
from typing import TYPE_CHECKING

from crewai.tools import tool
from core.db.qdrant_connector import QdrantConnector
from core.db.neo4j_connector import Neo4jConnector
from core.utils.zyte_client import ZyteClient

# Type imports for better IDE support
if TYPE_CHECKING:
    from bs4 import BeautifulSoup


# --- Placeholder Stubs for Sponsor Libraries ---

def generate_embedding_with_superlinked(product_data: dict) -> list[float]:
    """
    Generate vector embeddings for product data using Superlinked with fallback.
    
    This function first attempts to use Superlinked's embedding generation capabilities.
    If Superlinked is not available or fails, it falls back to sentence-transformers
    using the all-MiniLM-L6-v2 model for 384-dimensional embeddings.
    
    Args:
        product_data (dict): Product information including name, brand, price
        
    Returns:
        list[float]: Vector embedding for the product (384 dimensions)
    """
    from core.db.qdrant_connector import VECTOR_DIMENSION
    
    # Create meaningful text representation of the product
    product_text = _create_product_text(product_data)
    
    # Try Superlinked first (sponsor technology)
    try:
        import superlinked
        print(f"DEBUG: Using Superlinked for embedding: {product_data.get('name')}")
        # TODO: Implement actual Superlinked integration when API is available
        # For now, fall through to sentence-transformers
        raise ImportError("Superlinked integration pending")
        
    except (ImportError, Exception) as e:
        print(f"DEBUG: Superlinked unavailable ({e}), using sentence-transformers fallback")
        
        # Fallback to sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load the model (this will cache after first load)
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embedding
            embedding = model.encode(product_text, convert_to_tensor=False)
            
            # Ensure correct dimension
            if len(embedding) != VECTOR_DIMENSION:
                raise ValueError(f"Expected {VECTOR_DIMENSION} dimensions, got {len(embedding)}")
                
            return embedding.tolist()
            
        except Exception as fallback_error:
            print(f"ERROR: Fallback embedding generation failed: {fallback_error}")
            # Return zero vector as last resort
            return [0.0] * VECTOR_DIMENSION


def _create_product_text(product_data: dict) -> str:
    """
    Create a meaningful text representation of product data for embedding.
    
    Args:
        product_data (dict): Product information
        
    Returns:
        str: Formatted text representation
    """
    name = product_data.get('name', '').strip()
    brand = product_data.get('brand', '').strip()
    price = product_data.get('price', 0)
    category = product_data.get('category', '').strip()
    
    # Build descriptive text
    text_parts = []
    
    if brand:
        text_parts.append(f"Brand: {brand}")
    
    if name:
        text_parts.append(f"Product: {name}")
        
    if category:
        text_parts.append(f"Category: {category}")
        
    if price and price > 0:
        text_parts.append(f"Price range: ${price}")
    
    # Combine with natural language structure
    product_text = " | ".join(text_parts) if text_parts else "Unknown product"
    
    return product_text


def extract_product_info_with_cognee(raw_html: str) -> dict:
    """
    Extract structured product information from raw HTML using Cognee with fallback.
    
    This function first attempts to use Cognee's AI-powered content understanding.
    If Cognee is not available, it falls back to BeautifulSoup with pattern matching
    for common e-commerce site structures (Amazon, Flipkart, BigBasket, Swiggy, etc.).
    
    Args:
        raw_html (str): Raw HTML content from product pages
        
    Returns:
        dict: Structured product information
    """
    if not raw_html or not raw_html.strip():
        return _empty_product_info()
    
    # Try Cognee first (sponsor technology)
    try:
        import cognee
        print("DEBUG: Using Cognee for HTML extraction")
        # TODO: Implement actual Cognee integration when API is available
        # For now, fall through to BeautifulSoup
        raise ImportError("Cognee integration pending")
        
    except (ImportError, Exception) as e:
        print(f"DEBUG: Cognee unavailable ({e}), using BeautifulSoup fallback")
        return _extract_with_beautifulsoup(raw_html)


def _extract_with_beautifulsoup(raw_html: str) -> dict:
    """
    Extract product information using BeautifulSoup with e-commerce site patterns.
    
    Args:
        raw_html (str): Raw HTML content
        
    Returns:
        dict: Extracted product information
    """
    try:
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(raw_html, 'lxml')
        
        # Detect platform and use appropriate extraction strategy
        platform = _detect_platform(raw_html, soup)
        
        if platform == 'amazon':
            return _extract_amazon_product(soup)
        elif platform == 'flipkart':
            return _extract_flipkart_product(soup)
        elif platform == 'bigbasket':
            return _extract_bigbasket_product(soup)
        elif platform == 'swiggy':
            return _extract_swiggy_product(soup)
        else:
            # Generic extraction for unknown platforms
            return _extract_generic_product(soup)
            
    except Exception as e:
        print(f"ERROR: BeautifulSoup extraction failed: {e}")
        return _empty_product_info()


def _detect_platform(raw_html: str, soup: "BeautifulSoup") -> str:
    """Detect the e-commerce platform from HTML content."""
    html_lower = raw_html.lower()
    
    if 'amazon' in html_lower or soup.find(attrs={'data-asin': True}):
        return 'amazon'
    elif 'flipkart' in html_lower or soup.find(class_=lambda x: x and 'flipkart' in x.lower()):
        return 'flipkart'
    elif 'bigbasket' in html_lower:
        return 'bigbasket'
    elif 'swiggy' in html_lower:
        return 'swiggy'
    else:
        return 'generic'


def _extract_amazon_product(soup: "BeautifulSoup") -> dict:
    """Extract product info from Amazon pages."""
    product_info = _empty_product_info()
    
    # Product name
    name_selectors = [
        '#productTitle',
        '.product-title',
        '[data-automation-id="product-title"]'
    ]
    product_info['name'] = _extract_text_by_selectors(soup, name_selectors)
    
    # Brand
    brand_selectors = [
        '.po-brand .po-break-word',
        '#bylineInfo',
        '.brand'
    ]
    product_info['brand'] = _extract_text_by_selectors(soup, brand_selectors)
    
    # Price
    price_selectors = [
        '.a-price-whole',
        '.a-price .a-offscreen',
        '.apexPriceToPay'
    ]
    price_text = _extract_text_by_selectors(soup, price_selectors)
    product_info['price'] = _parse_price(price_text)
    
    # SKU/ASIN
    asin_elem = soup.find(attrs={'data-asin': True})
    if asin_elem:
        product_info['sku'] = asin_elem.get('data-asin')
    
    return product_info


def _extract_flipkart_product(soup: "BeautifulSoup") -> dict:
    """Extract product info from Flipkart pages."""
    product_info = _empty_product_info()
    
    # Product name
    name_selectors = [
        '.B_NuCI',
        '.x-product-title-label',
        '._35KyD6'
    ]
    product_info['name'] = _extract_text_by_selectors(soup, name_selectors)
    
    # Brand
    brand_selectors = [
        '.G6XhBx',
        '._2Ix8N',
        '.brand-name'
    ]
    product_info['brand'] = _extract_text_by_selectors(soup, brand_selectors)
    
    # Price
    price_selectors = [
        '._30jeq3._16Jk6d',
        '._1_WHN1',
        '.CEmiEU'
    ]
    price_text = _extract_text_by_selectors(soup, price_selectors)
    product_info['price'] = _parse_price(price_text)
    
    return product_info


def _extract_bigbasket_product(soup: "BeautifulSoup") -> dict:
    """Extract product info from BigBasket pages."""
    product_info = _empty_product_info()
    
    # Product name
    name_selectors = [
        '.product-title',
        '.pdp-product-name',
        'h1'
    ]
    product_info['name'] = _extract_text_by_selectors(soup, name_selectors)
    
    # Brand
    brand_selectors = [
        '.product-brand',
        '.brand-name'
    ]
    product_info['brand'] = _extract_text_by_selectors(soup, brand_selectors)
    
    # Price
    price_selectors = [
        '.discounted-price',
        '.selling-price',
        '.price'
    ]
    price_text = _extract_text_by_selectors(soup, price_selectors)
    product_info['price'] = _parse_price(price_text)
    
    return product_info


def _extract_swiggy_product(soup: "BeautifulSoup") -> dict:
    """Extract product info from Swiggy pages."""
    product_info = _empty_product_info()
    
    # For Swiggy (food delivery), structure is different
    name_selectors = [
        '.item-name',
        '.food-item-name',
        'h3', 'h2'
    ]
    product_info['name'] = _extract_text_by_selectors(soup, name_selectors)
    
    # Restaurant as "brand"
    brand_selectors = [
        '.restaurant-name',
        '.outlet-name'
    ]
    product_info['brand'] = _extract_text_by_selectors(soup, brand_selectors)
    
    # Price
    price_selectors = [
        '.item-price',
        '.rupee'
    ]
    price_text = _extract_text_by_selectors(soup, price_selectors)
    product_info['price'] = _parse_price(price_text)
    
    return product_info


def _extract_generic_product(soup: "BeautifulSoup") -> dict:
    """Generic extraction for unknown e-commerce platforms."""
    product_info = _empty_product_info()
    
    # Generic name extraction
    name_selectors = [
        'h1', 'h2',
        '[class*="title"]',
        '[class*="name"]',
        '[class*="product"]'
    ]
    product_info['name'] = _extract_text_by_selectors(soup, name_selectors)
    
    # Generic price extraction
    price_selectors = [
        '[class*="price"]',
        '[class*="cost"]',
        '[class*="amount"]'
    ]
    price_text = _extract_text_by_selectors(soup, price_selectors)
    product_info['price'] = _parse_price(price_text)
    
    # Try to find brand in common locations
    brand_selectors = [
        '[class*="brand"]',
        '[class*="manufacturer"]'
    ]
    product_info['brand'] = _extract_text_by_selectors(soup, brand_selectors)
    
    return product_info


def _extract_text_by_selectors(soup: "BeautifulSoup", selectors: list) -> str:
    """Try multiple CSS selectors and return first non-empty result."""
    for selector in selectors:
        try:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        except Exception:
            continue
    return ""


def _parse_price(price_text: str) -> float:
    """Extract numeric price from text."""
    if not price_text:
        return 0.0
    
    # Remove currency symbols and extract numbers
    import re
    numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
    
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            pass
    
    return 0.0


def _empty_product_info() -> dict:
    """Return empty product info structure."""
    return {
        "name": "",
        "brand": "",
        "price": 0.0,
        "sku": "",
        "category": "",
        "availability": "unknown"
    }


# --- CrewAI Tools Definition ---

@tool("Find Similar Products")
def find_similar_products_in_qdrant(product_name: str, product_brand: str = "", product_price: float = 0.0) -> str:
    """
    Find similar products in the vector database using product information.
    
    This tool performs semantic similarity search to find products that match
    the user's cart items. It uses vector embeddings to find semantically
    similar products even when exact names don't match.
    
    Args:
        product_name (str): Name/title of the product to search for
        product_brand (str, optional): Brand name for more precise matching
        product_price (float, optional): Price for additional context
        
    Returns:
        str: Human-readable summary of search results with product IDs and scores
    """
    try:
        # Prepare product data for embedding generation
        product_data = {
            "name": product_name,
            "brand": product_brand,
            "price": product_price
        }
        
        # Generate embedding for similarity search
        embedding = generate_embedding_with_superlinked(product_data)
        
        # Perform vector search in Qdrant
        qdrant = QdrantConnector()
        search_results = qdrant.search(vector=embedding, limit=3)
        
        if not search_results:
            return f"No similar products found in the vector database for '{product_name}'. The database may be empty or need to be populated with product data."
        
        # Format results for AI agent consumption
        summary = f"Found {len(search_results)} similar products for '{product_name}':\n"
        for result in search_results:
            summary += f"- Product ID: {result.payload.get('productId')}, Score: {result.score:.4f}\n"
        
        return summary
        
    except Exception as e:
        return f"Vector database search failed for '{product_name}': {e}. This may indicate the database needs initialization or configuration."


@tool("Scrape Product Page")
def scrape_product_page(url: str, country_code: str = "US") -> str:
    """
    Scrape product information from a given URL using geolocation.
    
    This tool fetches real-time product data from e-commerce websites
    using geolocation to get region-specific pricing and availability.
    
    Args:
        url (str): Target product page URL to scrape
        country_code (str, optional): 2-letter country code for geolocation (default: "US")
        
    Returns:
        str: Human-readable summary of scraped product information
    """
    # Try Zyte API first (premium option)
    zyte_result = _try_zyte_scraping(url, country_code)
    if zyte_result:
        return zyte_result
    
    # Fallback to direct HTTP request
    fallback_result = _try_direct_scraping(url)
    if fallback_result:
        return fallback_result
        
    # If both fail, return informative message
    return f"Unable to access product page at {url}. Both premium and fallback scraping methods failed. This may be due to anti-bot measures or network issues."


def _try_zyte_scraping(url: str, country_code: str) -> str:
    """Try scraping with Zyte API."""
    try:
        zyte_client = ZyteClient()
        
        # Perform geolocation-aware scraping
        scrape_result = zyte_client.scrape_url(url, country_code)
        
        if not scrape_result or "httpResponseBody" not in scrape_result:
            return None
        
        # Extract structured data from raw HTML
        raw_html = scrape_result["httpResponseBody"]
        product_info = extract_product_info_with_cognee(raw_html)
        
        # Return formatted product information
        if product_info.get('name') and product_info.get('name').strip():
            return f"Product scraped (Zyte): {product_info.get('name', 'Unknown')} - Price: {product_info.get('price', 'N/A')} - Brand: {product_info.get('brand', 'N/A')}"
        else:
            return None
            
    except ValueError as e:
        # Handle missing API key gracefully
        if "ZYTE_API_KEY" in str(e):
            print("DEBUG: Zyte API key not configured, trying fallback method")
            return None
        else:
            print(f"DEBUG: Zyte configuration error: {e}")
            return None
    except Exception as e:
        print(f"DEBUG: Zyte scraping failed: {e}")
        return None


def _try_direct_scraping(url: str) -> str:
    """Fallback to direct HTTP request with basic headers."""
    try:
        import requests
        from urllib.parse import urlparse
        
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Extract structured data from raw HTML
            product_info = extract_product_info_with_cognee(response.text)
            
            if product_info.get('name') and product_info.get('name').strip():
                return f"Product scraped (Direct): {product_info.get('name', 'Unknown')} - Price: {product_info.get('price', 'N/A')} - Brand: {product_info.get('brand', 'N/A')}"
            else:
                # Try to extract basic info from URL and page title
                domain = urlparse(url).netloc
                return f"Accessed product page on {domain} but could not extract detailed product information. The page structure may require specialized parsing."
        else:
            return None
            
    except Exception as e:
        print(f"DEBUG: Direct scraping failed: {e}")
        return None


@tool("Get Product Prices from Knowledge Graph")
def get_product_prices_from_neo4j(product_id: str, postal_code: str = "") -> str:
    """
    Get product prices from the Neo4j knowledge graph filtered by postal code.
    
    This tool queries the price graph to find historical and current pricing
    information for known products, filtered by geographic location for
    regional price variations.
    
    Args:
        product_id (str): Unique identifier for the product in the knowledge graph
        postal_code (str, optional): Postal code for location-based price filtering
        
    Returns:
        str: Human-readable summary of price information across retailers
    """
    neo4j = Neo4jConnector()
    
    # Cypher query to find product prices with optional postal code filtering
    query = """
    MATCH (p:Product {productId: $product_id})-[:SOLD_AT]->(r:Retailer)
    OPTIONAL MATCH (p)-[price_rel:HAS_PRICE {postalCode: $postal_code}]->(r)
    RETURN p.name as productName, r.name as retailer, price_rel.price as price, 
           price_rel.currency as currency, price_rel.lastUpdated as lastUpdated
    """
    
    params = {"product_id": product_id, "postal_code": postal_code}
    results = neo4j.execute_query(query, params)
    
    if not results:
        return f"No price information found for product ID {product_id} at postal code {postal_code}."
    
    # Format price information for AI agent
    product_name = results[0]['productName']
    price_summary = f"Found prices for {product_name}:\n"
    
    for res in results:
        if res['price']:  # Only include entries with actual price data
            price_summary += f"- {res['retailer']}: {res['currency']} {res['price']} (Last updated: {res['lastUpdated']})\n"
    
    return price_summary