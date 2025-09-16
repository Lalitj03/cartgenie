from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

class OptimizeCartAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('optimize-cart')

    def test_view_returns_400_for_invalid_payload(self):
        """
        Test Case: The API returns a 400 Bad Request if the payload structure is invalid.
        """
        invalid_payload = {
            "userContext": {"country": "IN", "postalCode": "560001"},
            # Missing "sourceRetailer" and "items"
        }
        response = self.client.post(self.url, data=json.dumps(invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    @patch('api.views.CartOptimizationCrew')
    def test_view_triggers_crew_with_new_payload_structure(self, mock_crew_class):
        """
        Test Case: The API correctly handles the internationalized payload structure.
        """
        # Arrange
        mock_crew_instance = MagicMock()
        mock_crew_result = {"status": "success"}
        mock_crew_instance.kickoff.return_value = json.dumps(mock_crew_result)
        mock_crew_class.return_value.setup_crew.return_value = mock_crew_instance

        request_payload = {
            "userContext": {
                "country": "IN",
                "postalCode": "560001"
            },
            "sourceRetailer": "amazon.in",
            "items": [
                {
                    "productTitle": "OnePlus Nord CE 3",
                    "price": 25000.00,
                    "currency": "INR"
                }
            ]
        }

        expected_crew_input = {
            "userContext": {
                "country": "IN",
                "postalCode": "560001"
            },
            "sourceRetailer": "amazon.in",
            "items": [
                {
                    "productTitle": "OnePlus Nord CE 3",
                    "price": 25000.00,
                    "currency": "INR",
                    "quantity": 1
                }
            ]
        }

        # Act
        response = self.client.post(self.url, data=json.dumps(request_payload), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 200)
        mock_crew_class.assert_called_once_with(expected_crew_input)
        mock_crew_class.return_value.setup_crew.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()
        self.assertEqual(response.json(), mock_crew_result)
