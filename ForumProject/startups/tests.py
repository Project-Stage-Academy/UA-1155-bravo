from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from startups.models import Startup
from users.models import CustomUser

class StartupCreationTestCase(TestCase):
    def setUp(self):
        # Create a CustomUser for authentication
        self.user = CustomUser.objects.create_user(
            email='dummy@user.com',
            first_name='John',
            last_name='Doe',
            phone_number='+3801234567',
            password='password',
            is_active=True
        )
        
        # Get JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        # Set up the test client and authenticate with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        # Sample data for testing
        self.startup_data = [{
                'startup_name': 'Django Dribblers',
                'startup_industry': 'IT',
                'startup_phone': '+3801234567',
                'startup_country': 'UA',
                'startup_city': 'Lviv',
                'startup_address': 'I Franka 123'
            },
            {
                'startup_name': 'Python catchers',
                'startup_industry': 'IT',
                'startup_phone': '+3809632587',
                'startup_country': 'UA',
                'startup_city': 'Odessa',
                'startup_address': 'Deribasivska 45'
            },
            {
                'startup_name': '   Django Dribblers',
                'startup_industry': 'IT',
                'startup_phone': '+3801234567',
                'startup_country': 'UA',
                'startup_city': 'Lviv',
                'startup_address': 'I Franka 123'
            }
        ]

    def test_ok_create_startup(self):
        # Test successful creation of a Startup
        response = self.client.post(reverse('startups:startup-list'), self.startup_data[0], format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 1)
        self.assertEqual(Startup.objects.first().startup_name, 'Django Dribblers')

    def test_ok_create_two_startups(self):
        # Test successful creation of more than one Startups
        response = self.client.post(reverse('startups:startup-list'), self.startup_data[0], format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 1)
        
        response = self.client.post(reverse('startups:startup-list'), self.startup_data[1], format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 2)

        self.assertEqual(Startup.objects.filter(startup_name='Django Dribblers').exists(), True)
        self.assertEqual(Startup.objects.filter(startup_name='Python catchers').exists(), True)

    def test_fail_create_startup_duplicate_name(self):
        # Create a Startup with the given name
        Startup.objects.create(**self.startup_data[0])
        
        # Attempt to create a Startup with the same name
        response = self.client.post(reverse('startups:startup-list'), self.startup_data[0], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('startup_name', response.data)
        self.assertEqual(Startup.objects.count(), 1)

        # Attempt to create a Startup with the same name AND leading whitespaces
        response = self.client.post(reverse('startups:startup-list'), self.startup_data[2], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('startup_name', response.data)
        self.assertEqual(Startup.objects.count(), 1)
