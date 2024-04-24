from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken

from datetime import datetime
from rest_framework_simplejwt.tokens import AccessToken


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


class PasswordRecoveryTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@gmail.com', password='Pa88word_')

    def test_password_recovery_valid_email(self):
        url = reverse('users:password-recovery')
        data = {'email': 'test@gmail.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Email was sent successfully')

    def test_password_recovery_invalid_email(self):
        url = reverse('users:password-recovery')
        data = {'email': 'test1@gmail.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User does not exist')

    def test_password_recovery_missing_email(self):
        url = reverse('users:password-recovery')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_password_recovery_empty_email(self):
        url = reverse('users:password-recovery')
        data = {'email': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    def test_password_recovery_no_email_field(self):
        url = reverse('users:password-recovery')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_token_validity(self):
        refresh = RefreshToken.for_user(self.user)
        token = str(refresh.access_token)

        decoded_token = AccessToken(token)

        expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
        is_expired = expiration_time < datetime.utcnow()

        self.assertFalse(is_expired)

        url = reverse('users:password-reset', kwargs={'token': token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertEqual(response.data['success'], 'Enter new data')
