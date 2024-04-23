from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PostTests(APITestCase):

    @patch('users.utils.Util.send_email')
    def test_register_user(self, mock_email):
        """
        Ensure we can create a new user.
        """

        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        expected_data = {
            'id': 1,
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'phone_number': '+380974131765'
        }
        url = reverse('users:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)
        mock_email.assert_called()

    def test_register_user_invalid(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        url = reverse('users:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
