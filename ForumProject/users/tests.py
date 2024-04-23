from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class PostTests(APITestCase):

    def tearDown(self):
        CustomUser.objects.all().delete()
        super().tearDown()

    @patch('users.utils.Util.send_email')
    def test_register_user_valid_data(self, mock_email):
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

        url = reverse('users:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        mock_email.assert_called()

    def test_register_user_missing_fields(self):
        url = reverse('users:register')

        # missed first_name
        data = {
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed last_name
        data = {
            'first_name': 'Martin',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed email
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed password
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed password2
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed phone_number
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_email(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        url = reverse('users:register')

        data['email'] = 'daniels@ gmail.com'
        response = self.client.post(url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['email'] = 'daniels @gmail.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['email'] = 'daniels gmail.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['email'] = 'daniels'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['email'] = 'daniels%example.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_password(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'phone_number': '+380974131765'
        }

        url = reverse('users:register')

        # shorter than 8 symbols
        data['password'] = 'Root1$'
        data['password2'] = 'Root1$'
        response = self.client.post(url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed at least 1 digit
        data['password'] = 'Rootroot$'
        data['password2'] = 'Rootroot$'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed at least 1 uppercase letter
        data['password'] = 'rootroot1$'
        data['password2'] = 'rootroot1$'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed at least 1 lowercase letter
        data['password'] = 'ROOTROOT1$'
        data['password2'] = 'ROOTROOT1$'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missed at least 1 special symbol
        data['password'] = 'Rootroot1'
        data['password2'] = 'Rootroot1'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # password fields didn't match.
    def test_register_user_different_passwords(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot$1',
            'phone_number': '+380974131765'
        }

        url = reverse('users:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # invalid phone number.
    def test_register_user_invalid_phone(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
        }

        url = reverse('users:register')

        # too short
        data['phone_number'] = '+3809741317'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # too long
        data['phone_number'] = '+3809741317651236'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # non-numeric characters
        data['phone_number'] = '+380qwe31765'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # not a unique email
    def test_register_user_not_unique_email(self):
        data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }

        url = reverse('users:register')

        data['email'] = 'daniels@gmail.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data['email'] = 'daniels@gmail.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
