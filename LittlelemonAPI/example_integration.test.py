# Example integration test?
# https://apidog.com/articles/how-to-test-django-rest-framework/

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Order


class OrderAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user and authenticate
        self.user = self.create_test_user()
        self.client.force_authenticate(user=self.user)

    def create_test_user(self):
        from django.contrib.auth.models import User

        return User.objects.create_user(username="testuser", password="testpassword")

    def test_create_order(self):
        data = {
            "menu_item": 1,  # Assuming a menu item with ID 1 exists
            "quantity": 2,
            "special_request": "No onions",
        }
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
