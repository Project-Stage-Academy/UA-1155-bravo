from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from startups.models import Startup
from users.models import CustomUser
import random, string

class StartupCreationTestCase(TestCase):
    
    def setUp(self):
        '''
        Setting up pre-requisites for testing 
        '''
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
        self.startup_data = {
                            'startup_name': 'Django Dribblers',
                            'startup_industry': 'IT',
                            'startup_phone': '+3801234567',
                            'startup_country': 'UA',
                            'startup_city': 'Lviv',
                            'startup_address': 'I Franka 123'
                        }


    def test_ok_create_startup(self):
        '''
        Tested creation of one Startup
        '''
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 1)
        self.assertEqual(Startup.objects.first().startup_name, 'Django Dribblers')


    def test_ok_create_two_startups(self):
        '''
        Tested creation of two Startups
        '''
        # Create first Startup
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 1)
        
        # Create second Startup
        self.startup_data['startup_name'] = 'Python catchers'
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 2)

        self.assertEqual(Startup.objects.filter(startup_name='Django Dribblers').exists(), True)
        self.assertEqual(Startup.objects.filter(startup_name='Python catchers').exists(), True)

    
    def test_fail_create_startup_duplicate_name(self):
        '''
        Two cases are tested - with completele identical startup_name
        and with the startup_name having leading whitespaces but otherwie being identical
        '''
        # Create a Startup with the given name
        Startup.objects.create(**self.startup_data)
        
        # Attempt to create a Startup with the same name
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 1)

        # Attempt to create a Startup with the same name AND leading whitespaces
        self.startup_data['startup_name'] = '  ' + self.startup_data['startup_name']
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 1)

    
    def test_fail_field_length_exceeded(self):
        '''
        The function iterates over Startup's aattributes, each time assigning to 
        an attribute a value that exceeds the max_length restraint, and then the 
        test is run
        '''
        # retrieve from the Model values of mzx_length attributes
        max_length = {}
        fields = Startup._meta.fields
        for field in fields:
            if field.name in self.startup_data and hasattr(field, 'max_length') and field.max_length:
                max_length[field.name] = field.max_length
        
        # iterate over Startup's attributes, set up value exceeding the max_length and test
        for key, value in self.startup_data.items():
            original_value = self.startup_data[key]
            if key == 'startup_phone':
                self.startup_data[key] = '+' + ''.join(random.choices(string.digits, k=max_length[key] + 1))
            else:
                self.startup_data[key] = ''.join(random.choices(string.ascii_letters, k=max_length[key] + 1))
            response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Startup.objects.count(), 0)
            self.startup_data[key] = original_value

    
    def test_fail_invalid_phone(self):
        '''
        The function checks that creation of a Startup with invalid phone number fails
        '''
        # non-numeric symbols
        self.startup_data['startup_phone'] = '+123abc457891'
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 0)

        # absent leading '+' sign
        self.startup_data['startup_phone'] = '1234567891012'
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 0)

        # less than 9 digits (validator restraint fails)
        self.startup_data['startup_phone'] = '+1234'
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 0)

        # more than 17 digits (validator restraint fails)
        self.startup_data['startup_phone'] = '+23456789112345678'
        response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 0)


    def test_fail_field_mandatory_attr_empty(self):
        '''
        The function iterates over Startup's aattributes, each time assigning to 
        an attribute an empty string, and then the test is run
        '''
        for key, value in self.startup_data.items():
            original_value = self.startup_data[key]
            self.startup_data[key] = ''
            response = self.client.post(reverse('startups:startup-list'), self.startup_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Startup.objects.count(), 0)
            self.startup_data[key] = original_value