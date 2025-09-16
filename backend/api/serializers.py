"""
CartGenie API Serializers

This module defines the data serialization contracts for the CartGenie API.
It includes both request and response serializers to ensure consistent
data validation and formatting across the API endpoints.

Request Flow:
- Client sends cart data via OptimizeCartRequestSerializer
- API validates and processes the data
- AI agents generate recommendations
- Response formatted via OptimizeCartResponseSerializer

The serializers enforce data integrity and provide clear API documentation.
"""

from rest_framework import serializers


# --- Request Serializers ---

class CartItemSerializer(serializers.Serializer):
    """
    Serializer for individual cart items.
    
    Represents a single product in the user's shopping cart with
    all necessary information for price comparison and optimization.
    """
    productTitle = serializers.CharField(
        max_length=500,
        help_text="Full product name/title as displayed on the retailer site"
    )
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="Number of units of this product in the cart"
    )
    price = serializers.FloatField(
        min_value=0.0,
        help_text="Current price per unit in the specified currency"
    )
    currency = serializers.CharField(
        max_length=3,
        help_text="ISO 4217 currency code (e.g., 'INR', 'USD', 'EUR')"
    )
    url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Direct link to the product page (optional)"
    )


class UserContextSerializer(serializers.Serializer):
    """
    Serializer for user context information.
    
    Contains geographic and preference data needed for
    localized price comparisons and targeted recommendations.
    """
    country = serializers.CharField(
        max_length=2,
        help_text="ISO 3166-1 alpha-2 country code (e.g., 'IN', 'US')"
    )
    postalCode = serializers.CharField(
        max_length=10,
        help_text="Postal/ZIP code for regional price variations"
    )


class OptimizeCartRequestSerializer(serializers.Serializer):
    """
    Main request serializer for cart optimization endpoint.
    
    Combines user context, retailer information, and cart items
    to provide complete context for AI-powered optimization.
    """
    userContext = UserContextSerializer(
        help_text="User location and preference information"
    )
    sourceRetailer = serializers.CharField(
        max_length=100,
        help_text="Name or domain of the original retailer (e.g., 'amazon.in')"
    )
    items = CartItemSerializer(
        many=True,
        allow_empty=False,
        help_text="List of products currently in the user's cart"
    )


# --- Response Serializers (for documentation and consistency) ---

class RecommendationItemSerializer(serializers.Serializer):
    """
    Serializer for recommended product alternatives.
    
    Represents a cheaper alternative found by the AI agents,
    including all information needed for the user to make a decision.
    """
    productTitle = serializers.CharField(
        help_text="Title of the recommended alternative product"
    )
    price = serializers.FloatField(
        help_text="Price of the alternative product"
    )
    currency = serializers.CharField(
        max_length=3,
        help_text="Currency code for the alternative product price"
    )
    retailer = serializers.CharField(
        help_text="Name of the retailer offering this alternative"
    )
    url = serializers.URLField(
        help_text="Direct link to purchase the alternative product"
    )


class SavingsRecommendationSerializer(serializers.Serializer):
    """
    Serializer for savings recommendations.
    
    Pairs an original cart item with its best alternative,
    showing potential savings for each product.
    """
    originalItem = CartItemSerializer(
        help_text="The original product from the user's cart"
    )
    cheapestAlternative = RecommendationItemSerializer(
        help_text="The best alternative found by AI agents"
    )


class OptimizeCartResponseSerializer(serializers.Serializer):
    """
    Main response serializer for cart optimization results.
    
    Provides a comprehensive summary of potential savings including:
    - Total cost comparison (original vs optimized)
    - Per-item recommendations with alternatives
    - Clear savings calculations
    """
    originalTotal = serializers.FloatField(
        help_text="Total cost of the original cart"
    )
    optimizedTotal = serializers.FloatField(
        help_text="Total cost if all recommendations are followed"
    )
    currency = serializers.CharField(
        max_length=3,
        help_text="Currency for all monetary values in this response"
    )
    totalSavings = serializers.FloatField(
        help_text="Total amount saved (originalTotal - optimizedTotal)"
    )
    recommendations = SavingsRecommendationSerializer(
        many=True,
        help_text="List of per-item recommendations with alternatives"
    )