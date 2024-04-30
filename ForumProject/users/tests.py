from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser

class LogoutTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@gmail.com', password='Pa88word')
        cls.user.is_active = True
        cls.user.save()
        cls.url_token = reverse('users:token_obtain_pair')
        cls.url_logout = reverse('users:logout')

        client = Client()
        # Sending a request to obtain access tokens
        response = client.post(cls.url_token, {'email': cls.user.email, 'password': 'Pa88word'}, content_type="application/json")
        cls.access_token = response.data.get("access")
        cls.refresh_token = response.data.get("refresh")

    def test_logout_success(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = self.client.post(self.url_logout, content_type="application/json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User successfully logged out.")
