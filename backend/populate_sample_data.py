#!/usr/bin/env python3
"""
Sample Data Populator for CartGenie

This script populates the Qdrant vector database with sample product data
to demonstrate the price comparison functionality when testing the system.

Usage:
    python populate_sample_data.py

This will add sample products across different categories with embeddings
for similarity search testing.
"""

import sys
import os
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-sample-data')
os.environ.setdefault('QDRANT_HOST', 'localhost')
os.environ.setdefault('QDRANT_PORT', '6333')

def populate_sample_products():
    """Populate Qdrant with sample product data for testing."""
    try:
        from core.db.qdrant_connector import QdrantConnector
        from core.agents.tools import generate_embedding_with_superlinked
        from qdrant_client import models
        
        # Sample products across different categories
        sample_products = [
            {
                "productId": "WOODLAND_SHOES_001",
                "name": "Woodland Men's Leather Casual Shoes Brown",
                "brand": "Woodland",
                "category": "Footwear",
                "price": 3299.0,
                "currency": "INR",
                "retailer": "Amazon India",
                "url": "https://amazon.in/woodland-shoes"
            },
            {
                "productId": "WOODLAND_SHOES_002", 
                "name": "Woodland Men Camel Outdoor Shoes",
                "brand": "Woodland",
                "category": "Footwear",
                "price": 3199.0,
                "currency": "INR",
                "retailer": "Flipkart",
                "url": "https://flipkart.com/woodland-shoes"
            },
            {
                "productId": "SONY_HEADPHONES_001",
                "name": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
                "brand": "Sony",
                "category": "Electronics",
                "price": 29990.0,
                "currency": "INR",
                "retailer": "Amazon India",
                "url": "https://amazon.in/sony-headphones"
            },
            {
                "productId": "SONY_HEADPHONES_002",
                "name": "Sony WH-1000XM5 Headphones Black",
                "brand": "Sony", 
                "category": "Electronics",
                "price": 28999.0,
                "currency": "INR",
                "retailer": "Flipkart",
                "url": "https://flipkart.com/sony-headphones"
            },
            {
                "productId": "IPHONE_001",
                "name": "Apple iPhone 15 Pro Natural Titanium 128GB",
                "brand": "Apple",
                "category": "Smartphones",
                "price": 134900.0,
                "currency": "INR",
                "retailer": "Amazon India",
                "url": "https://amazon.in/iphone-15-pro"
            },
            {
                "productId": "ALMONDS_001",
                "name": "Organic Raw Almonds Premium Quality 1kg",
                "brand": "Nature's Best",
                "category": "Groceries",
                "price": 899.0,
                "currency": "INR",
                "retailer": "BigBasket",
                "url": "https://bigbasket.com/almonds"
            }
        ]
        
        # Connect to Qdrant
        qdrant = QdrantConnector()
        
        # Prepare points for insertion
        points = []
        
        print("Generating embeddings and preparing data points...")
        
        for product in sample_products:
            # Generate embedding for the product
            embedding = generate_embedding_with_superlinked(product)
            
            # Create Qdrant point
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=product
            )
            points.append(point)
            
            print(f"  ✅ Prepared: {product['name']}")
        
        # Insert points into Qdrant
        print(f"\nInserting {len(points)} products into Qdrant...")
        qdrant.upsert_points(points)
        
        print(f"✅ Successfully populated {len(sample_products)} sample products!")
        print("\nSample products added:")
        for product in sample_products:
            print(f"  - {product['name']} ({product['retailer']}: {product['currency']} {product['price']})")
            
        print(f"\n🎉 Vector database is now ready for testing!")
        print("You can now test similarity search with products like 'Woodland Men Camel Shoes'")
        
    except Exception as e:
        print(f"❌ Failed to populate sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("CartGenie Sample Data Populator")
    print("=" * 50)
    populate_sample_products()