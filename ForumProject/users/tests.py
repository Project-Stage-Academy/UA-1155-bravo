from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

class LogoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        # Create user
        self.client.post(reverse("users:create"), self.user_data, content_type="application/json")
        # Get access
        response = self.client.post(reverse("token_obtain_pair"), self.user_data, content_type="application/json")
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def test_logout_success(self):
        url = reverse("logout")
        headers = {
            "Authorization": f"Bearer {self.refresh_token}",
            "Content-Type": "application/json",
        }
        response = self.client.post(url, content_type="application/json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User successfully logged out.")

    def test_logout_invalid_token(self):
        url = reverse("logout")
        headers = {
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json",
        }
        response = self.client.post(url, content_type="application/json", **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")
