from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class PostTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.base_data = {
            'first_name': 'Martin',
            'last_name': 'Daniels',
            'email': 'daniels@gmail.com',
            'password': 'Rootroot1$',
            'password2': 'Rootroot1$',
            'phone_number': '+380974131765'
        }
        self.url = reverse('users:register')

    def tearDown(self):
        CustomUser.objects.all().delete()
        super().tearDown()

    def case_fields(self, data, field_to_update):
        for item in data:
            with self.subTest(item=item):
                data = self.base_data.copy()
                data[field_to_update] = item
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.utils.Util.send_email')
    def test_register_user_valid_data(self, mock_email):
        response = self.client.post(self.url, self.base_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        mock_email.assert_called()

    def test_register_missing_field(self):
        for field in self.base_data:
            with self.subTest(field=field):
                data = self.base_data.copy()
                del data[field]
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        invalid_emails = [
            'daniels@ gmail.com',
            'daniels @gmail.com',
            'daniels gmail.com',
            'daniels',
            'daniels%example.com',
            'd'*100+'gmail.com'
        ]
        self.case_fields(invalid_emails, 'email')

    def test_register_invalid_password(self):
        invalid_passwords = [
            ('Root1$', 'Root1$'),
            ('Rootroot$', 'Rootroot$'),
            ('rootroot1$', 'rootroot1$'),
            ('ROOTROOT1$', 'ROOTROOT1$'),
            ('Rootroot1', 'Rootroot1'),
            ('Rootroot1$', 'Rootroot$1')
        ]
        for password in invalid_passwords:
            with self.subTest(password=password):
                data = self.base_data.copy()
                data['password'] = password[0]
                data['password2'] = password[1]
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_phone_number(self):
        invalid_phone_numbers = [
            '+3809741317',
            '+3809741317651236',
            '+380qwe31765',
        ]
        self.case_fields(invalid_phone_numbers, 'phone_number')

    def test_register_user_not_unique_email(self):
        response = self.client.post(self.url, self.base_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.base_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_first_name_max_length(self):
        data = self.base_data.copy()
        data['first_name'] = 'q'*21
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_last_name_max_length(self):
        data = self.base_data.copy()
        data['last_name'] = 'q'*21
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
