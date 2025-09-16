"""
CartGenie API Views

This module contains the main API endpoints for the CartGenie shopping optimization service.
The primary endpoint accepts shopping cart data and returns AI-powered savings recommendations.
"""

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OptimizeCartRequestSerializer
from core.agents.crew import CartOptimizationCrew


class OptimizeCartView(APIView):
    """
    API endpoint that receives a user's shopping cart and returns an optimized savings plan.
    
    This view handles the main cart optimization workflow:
    1. Validates incoming cart data against the API schema
    2. Initializes CrewAI agents to research products and analyze savings
    3. Returns structured recommendations with potential savings
    
    Expected request format:
    {
        "userContext": {"country": "IN", "postalCode": "560001"},
        "sourceRetailer": "amazon.in",
        "items": [{"productTitle": "...", "price": 100, "currency": "INR", ...}]
    }
    
    Response format includes original/optimized totals and per-item recommendations.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Process a cart optimization request.
        
        Args:
            request: Django REST framework request containing cart data
            
        Returns:
            Response: JSON response with optimization results or error details
        """
        # Step 1: Validate the incoming cart data against our schema
        serializer = OptimizeCartRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            # Step 2: Initialize the AI crew with user context and cart data
            crew_manager = CartOptimizationCrew(validated_data)
            crew = crew_manager.setup_crew()

            # Step 3: Execute the AI workflow (research → analysis → recommendations)
            result_json_string = crew.kickoff()

            # Step 4: Parse the AI-generated result and return structured response
            result_data = json.loads(result_json_string)

            return Response(result_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            # Handle cases where AI crew returns malformed JSON
            print(f"ERROR: Failed to parse AI crew result as JSON: {e}")
            return Response(
                {"error": "Invalid response format from AI processing."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Catch any unexpected errors during the crew's execution
            print(f"ERROR: An unexpected error occurred in the AI crew: {e}")
            return Response(
                {"error": "An internal error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
