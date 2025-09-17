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
    
    def _clean_json_from_markdown(self, text: str) -> str:
        """
        Clean markdown code block markers from JSON string.
        
        AI agents often return JSON wrapped in markdown code blocks like:
        ```json
        {"key": "value"}
        ```
        
        This method extracts the actual JSON content.
        
        Args:
            text (str): Raw text that may contain markdown-wrapped JSON
            
        Returns:
            str: Clean JSON string ready for parsing
        """
        import re
        
        # Remove markdown code block markers
        # Handle both ```json and ``` variants
        text = text.strip()
        
        # Remove opening code block markers
        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
        
        # Remove closing code block markers
        text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up any remaining whitespace
        text = text.strip()
        
        return text
    
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
            crew_output = crew.kickoff()

            # Step 4: Extract the string result from CrewOutput object
            if hasattr(crew_output, 'raw'):
                result_json_string = crew_output.raw
            elif hasattr(crew_output, 'output'):
                result_json_string = crew_output.output
            elif hasattr(crew_output, 'text'):
                result_json_string = crew_output.text
            else:
                # Fallback: convert CrewOutput to string
                result_json_string = str(crew_output)

            # Step 5: Clean markdown code blocks from JSON string
            cleaned_json_string = self._clean_json_from_markdown(result_json_string)

            # Step 6: Parse the AI-generated result and return structured response
            result_data = json.loads(cleaned_json_string)

            return Response(result_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            # Handle cases where AI crew returns malformed JSON
            print(f"ERROR: Failed to parse AI crew result as JSON: {e}")
            print(f"Raw crew output: {crew_output if 'crew_output' in locals() else 'Not available'}")
            print(f"Cleaned JSON string: {cleaned_json_string if 'cleaned_json_string' in locals() else 'Not available'}")
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
