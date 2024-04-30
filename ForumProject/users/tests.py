from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistration(APITestCase):
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


class PasswordResetViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@gmail.com', password='Pa88word_')
        cls.token = RefreshToken.for_user(cls.user).access_token

    def test_successful_password_reset(self):
        new_password = 'NewPa55word_'
        url = reverse('users:password-reset', args=(self.token,))
        data = {'password': new_password, 'password2': new_password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertEqual(response.data['success'], 'Password has been successfully updated')
        updated_user = CustomUser.objects.get(email='test@gmail.com')
        self.assertTrue(updated_user.check_password(new_password))

    def test_password_reset_with_mismatched_passwords(self):
        new_password = 'NewPa55word_'
        url = reverse('users:password-reset', args=(self.token,))
        data = {'password': new_password, 'password2': 'DifferentPa55word_'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Password fields didn't match.", response.data['password2'])
        unchanged_user = CustomUser.objects.get(email='test@gmail.com')
        self.assertTrue(unchanged_user.check_password('Pa88word_'))

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], 'User does not exist')

    def test_password_recovery_missing_email(self):
        url = reverse('users:password-recovery')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_password_recovery_empty_email(self):
        url = reverse('users:password-recovery')
        data = {'email': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    def test_password_recovery_no_email_field(self):
        url = reverse('users:password-recovery')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)

    @patch('users.views.jwt.decode')
    def test_invalid_token(self, mock_decode):
        token = 'valid_token'
        url = reverse('users:password-reset', args=(token,))
        mock_decode.return_value = {'user_id': self.user.id + 1}
        data = {'password': 'Pa88word_2', 'password2': 'Pa88word_2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Invalid token')


class TokenObtainPairViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@gmail.com', password='Pa88word_')
        cls.user.is_active = True
        cls.user.save()
        cls.url = reverse('users:token_obtain_pair')

    def test_sign_in_with_valid_credentials(self):
        data = {'email': 'test@gmail.com', 'password': 'Pa88word_'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_sign_in_with_invalid_email(self):
        data = {'email': 'test1@gmail.com', 'password': 'Pa88word_'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sign_in_with_invalid_password(self):
        data = {'email': 'test@gmail.com', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sign_in_missing_email(self):
        data = {'password': 'Pa88word_'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sign_in_missing_password(self):
        data = {'email': 'test@gmail.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
