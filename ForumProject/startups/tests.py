from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from startups.models import Startup
from investors.models import Investor
from users.models import CustomUser, UserStartup, UserRoleCompany, UserInvestor
import random, string
from django.db import transaction
from rest_framework.test import APITestCase
from projects.models import Project
from django.core.exceptions import ObjectDoesNotExist

class StartupCreationTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        '''
        Setting up test data that does not change across tests.
        '''
        # Create a CustomUser for authentication
        cls.user = CustomUser.objects.create_user(
            email='smarter@leon.com',
            first_name='Harry',
            last_name='Potter',
            phone_number='+380948567',
            password='harrypotter',
            is_active=True
        )
        
        # Get JWT token for the user
        refresh = RefreshToken.for_user(cls.user)
        cls.token = str(refresh.access_token)

        cls.investor_user = CustomUser.objects.create_user(
                        email='example@investor.com',
                        first_name='examinv',
                        last_name='example',
                        phone_number='+3804251633',
                        password='example',
                        is_active=True
                )

        refresh_investor = RefreshToken.for_user(cls.investor_user)
        cls.investor_token = str(refresh_investor.access_token)
    
    
    def setUp(self):
        '''
        Setup that is executed before each test case.
        '''
        # Set up the test client and authenticate with the token
        self.client = APIClient()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Sample data for testing
        self.startup = Startup.objects.create(startup_name='Django startups',
                                              startup_industry='Games',
                                              startup_phone='+3801234111',
                                              startup_country='UG',
                                              startup_city='Londoni',
                                              startup_address='Kulparkivska')
        
        UserStartup.objects.create(customuser=self.user, startup=self.startup, startup_role_id=1)
        UserRoleCompany.objects.create(user=self.user, role='startup', company_id=self.startup.id)
        

        # Sample data for testing
        self.startup_data = {
            'startup_name': 'defaultstartup',
            'startup_industry': 'default',
            'startup_phone': '+3801455645',
            'startup_country': 'UA',
            'startup_city': 'default',
            'startup_address': 'default 123'
        }
    
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        
        # Create investor profile
        self.investor_profile = Investor.objects.create(
            investor_name='Nature Investor',
            investor_industry='Nature',
            investor_phone='+3801999655',
            investor_country='UA',
            investor_city='Nature City',
            investor_address='Nature Address'
        )
        
        # Associate investor profile with investor user and assign role
        UserInvestor.objects.create(customuser=self.investor_user, investor=self.investor_profile, investor_role_id=1)
        UserRoleCompany.objects.create(user=self.investor_user, role='investor', company_id=self.investor_profile.id)


    def tearDown(self):
        '''
        Teardown that is executed after each test case.
        '''
        CustomUser.objects.all().delete()
        Investor.objects.all().delete()
        Startup.objects.all().delete()
        UserInvestor.objects.all().delete()
        UserStartup.objects.all().delete()
        UserRoleCompany.objects.all().delete()
        
    
    def create_startup(self, startup_data):
        '''
        Helper method to create a Startup with given data.
        '''
        url = reverse('startups:startup-add')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        created = self.client.post(url, startup_data, format='json')
        return created
    
    
    def assert_failure(self, startup_data, expected_objects=1):
        '''
        Helper method to verify the Startup creation fails as expected
        '''
        response = self.create_startup(startup_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), expected_objects)

    def test_ok_create_startup(self):
        '''
        Tested creation of one Startup.
        '''
        response = self.create_startup(self.startup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 2) #created in SetUp and in test exsists 
        self.assertEqual(Startup.objects.all()[1].startup_name, 'Defaultstartup')

    @transaction.atomic
    def test_ok_create_two_startups(self):
        '''
        Tested creation of two Startups
        '''
        # Create first Startup
        response = self.create_startup(self.startup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 2)
        
        # Create second Startup
        self.startup_data['startup_name'] = 'Python catchers'
        response = self.create_startup(self.startup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 3)

        self.assertEqual(Startup.objects.filter(startup_name='Defaultstartup').exists(), True)
        self.assertEqual(Startup.objects.filter(startup_name='Python catchers').exists(), True)

    @transaction.atomic
    def test_fail_create_startup_duplicate_name(self):
        '''
        Two cases are tested - with completele identical startup_name
        and with the startup_name having leading whitespaces but otherwie being identical
        '''
        # Create a Startup with the given name
        Startup.objects.create(**self.startup_data)
        
        # Attempt to create a Startup with the same name
        self.assert_failure(self.startup_data, 2) #created in SetUp and in test exsists 

        # Attempt to create a Startup with the same name AND leading whitespaces
        self.startup_data['startup_name'] = '  ' + self.startup_data['startup_name']
        self.assert_failure(self.startup_data, 2) #created in SetUp and in test exsists, with name '  ' doesnt

    @transaction.atomic
    def test_fail_field_length_exceeded(self):
        '''
        The function iterates over Startup's attributes, each time assigning to 
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
            self.assert_failure(self.startup_data)
            self.startup_data[key] = original_value

    @transaction.atomic
    def test_fail_invalid_phone(self):
        '''
        The function checks that creation of a Startup with invalid phone number fails
        '''
        # non-numeric symbols
        self.startup_data['startup_phone'] = '+123abc457891'
        self.assert_failure(self.startup_data)

        # absent leading '+' sign
        self.startup_data['startup_phone'] = '1234567891012'
        self.assert_failure(self.startup_data)

        # less than 9 digits (validator restraint fails)
        self.startup_data['startup_phone'] = '+1234'
        self.assert_failure(self.startup_data)

        # more than 17 digits (validator restraint fails)
        self.startup_data['startup_phone'] = '+23456789112345678'
        self.assert_failure(self.startup_data)

    @transaction.atomic
    def test_fail_field_mandatory_attr_empty(self):
        '''
        The function iterates over Startup's aattributes, each time assigning to 
        an attribute an empty string, and then the test is run
        '''
        for key, value in self.startup_data.items():
            original_value = self.startup_data[key]
            self.startup_data[key] = ''
            self.assert_failure(self.startup_data)
            self.startup_data[key] = original_value
            
    def test_create_startup(self):
        '''
        The function tests the creation of a new startup through the API.
        '''
        url = reverse('startups:startup-add')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(url, self.startup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Startup.objects.count(), 2)
        

    def test_create_startup_missing_fields(self):
        '''
        Test creating a new startup with missing fields via API.
        '''
        incomplete_data = {
            'startup_name': 'Incomplete Startup',
            'startup_industry': 'IT',
            'startup_country': 'US',
            'startup_city': 'New York',
            'startup_address': '123 Main St'
        }
        url = reverse('startups:startup-add')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Startup.objects.count(), 1)  #only startup created in SetUp



    def test_delete_startup(self):
        '''
        Test deleting a startup via API.
        '''
        # Create a startup
        self.created_startup = Startup.objects.create(**self.startup_data)
        UserStartup.objects.create(customuser=self.user, startup=self.created_startup, startup_role_id=1)
        url = reverse('startups:startup-detail', kwargs={'pk': self.created_startup.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Startup.objects.count(), 1) #Only created in SetUp exsist 
        

    def test_delete_startup_with_closed_projects(self):
        '''
        Test deleting a startup with closed projects via API.
        '''
        self.startup = Startup.objects.create(**self.startup_data)
        UserStartup.objects.create(customuser=self.user, startup=self.startup, startup_role_id=1)
        # Create a closed project associated with the startup
        # Project.objects.create(startup=startup, project_name='Closed Project', project_status='closed')
        Project.objects.create(
                startup=self.startup,
                name='Closed Project',
                status='closed',
                description='Description of the project',
                duration=6,  
                budget_currency='USD',
                budget_amount=5000
            )
        url = reverse('startups:startup-detail', kwargs={'pk': self.startup.pk}) 
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Startup.objects.count(), 1) #Only created in SetUp exsist 


    def test_delete_startup_with_open_projects(self):
        '''
        Test deleting a startup with open projects via API.
        '''
        self.startup = Startup.objects.create(**self.startup_data)
        # Create an open project associated with the startup
        Project.objects.create(
                startup=self.startup,
                name='Open Project',
                status='open',
                description='Description of the project',
                duration=6,  
                budget_currency='USD',
                budget_amount=5000
            )
        url = reverse('startups:startup-detail', kwargs={'pk': self.startup.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Startup.objects.count(), 2)  #created in SetUp and in test exsists 
        
         
        
    # filters search
        
    @transaction.atomic
    def test_search_startup(self):
        '''
        Test searching for startups via API.
        '''

        Startup.objects.create(startup_name='zxcvb', 
                               startup_industry='Vanish', 
                               startup_phone='+1234567890', 
                               startup_country='AG', 
                               startup_city='New York', 
                               startup_address='123 Main St')
        Startup.objects.create(startup_name='TestStartup1', 
                               startup_industry='Vanish', 
                               startup_phone='+1234567890',
                               startup_country='AG', 
                               startup_city='New York', 
                               startup_address='123 Main St')
        

        url = reverse('startups:startup-search') + '?search=Test'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['startup_name'], 'TestStartup1')
        
        
        
    @transaction.atomic
    def test_filter_startup_by_country(self):
        '''
        Test filtering startups by country via API.
        '''
        for i in range(15):
            Startup.objects.create(startup_name=f'Test Startup {i}', 
                                   startup_industry='Vanish', 
                                   startup_phone='+1234567890', 
                                   startup_country='UA', 
                                   startup_city='New York', 
                                   startup_address='123 Main St')
        for b in range(4):
            Startup.objects.create(startup_name=f'Startup{b}', 
                                startup_industry='Vanish', 
                                startup_phone='+1234567890', 
                                startup_country='US', 
                                startup_city='New York', 
                                startup_address='123 Main St')

        url = reverse('startups:startup-list') + '?startup_name=&startup_industry=&project_status=&startup_country=US'  
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  

    
    @transaction.atomic
    def test_startup_pagination(self):
        '''
        Test pagination of startups via API.
        '''
        for i in range(15):
            Startup.objects.create(startup_name=f'Test Startup {i}', 
                                   startup_industry='Vanish', 
                                   startup_phone='+1234567890', 
                                   startup_country='US', 
                                   startup_city='New York', 
                                   startup_address='123 Main St')
        

        url = reverse('startups:startup-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  


        url = reverse('startups:startup-list') + '?page_size=5'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  
        



class StartupViewSetTestCase(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        '''
        Setting up test data that does not change across tests.
        '''
        # Create a CustomUser for authentication
        cls.user = CustomUser.objects.create_user(
            email='dummy@user.com',
            first_name='Alex',
            last_name='Leon',
            phone_number='+3801274120',
            password='alexleon',
            is_active=True
        )
        
        # Get JWT token for the user
        refresh = RefreshToken.for_user(cls.user)
        cls.token = str(refresh.access_token)   
        
        cls.investor_user = CustomUser.objects.create_user(
                    email='investor@example.com',
                    first_name='Investor',
                    last_name='User',
                    phone_number='+3801234567',
                    password='password',
                    is_active=True
            )

        refresh_investor = RefreshToken.for_user(cls.investor_user)
        cls.investor_token = str(refresh_investor.access_token)
        
    def setUp(self):
        '''
        Setup that is executed before each test case.
        '''
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        
        # Create investor profile
        self.investor_profile = Investor.objects.create(
            investor_name='Inv examlpe',
            investor_industry='Test',
            investor_phone='+3802222231',
            investor_country='UG',
            investor_city='Inv examlpe',
            investor_address='Inv examlpe 2'
        )
        
        # Associate investor profile with investor user and assign role
        UserInvestor.objects.create(customuser=self.investor_user, investor=self.investor_profile, investor_role_id=1)
        UserRoleCompany.objects.create(user=self.investor_user, role='investor', company_id=self.investor_profile.id)
        # Set up the test client and authenticate with the token
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Sample data for testing
        self.startup = Startup.objects.create(startup_name='Django Dribblers',
                                              startup_industry='IT',
                                              startup_phone='+3801234567',
                                              startup_country='UA',
                                              startup_city='Lviv',
                                              startup_address='I Franka 123')
        
        UserStartup.objects.create(customuser=self.user, startup=self.startup, startup_role_id=1)
        UserRoleCompany.objects.create(user=self.user, role='startup', company_id=self.startup.id)
        
    def tearDown(self):
        '''
        Teardown that is executed after each test case.
        '''
        CustomUser.objects.all().delete()
        Investor.objects.all().delete()
        Startup.objects.all().delete()
        UserInvestor.objects.all().delete()
        UserStartup.objects.all().delete()
        UserRoleCompany.objects.all().delete()
        

    def test_retrieve_startup_list(self):
        '''
        Test retrieving the list of startups
        '''        
        # Checking availability of the startup list
        retrieve_startup_list = reverse('startups:startup-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(retrieve_startup_list)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Startup.objects.count(), 1)
    

    def test_retrieve_single_startup(self):
        '''
        Test retrieving a single startup
        '''
        # Checking availability of a single startup
        response = self.client.get(reverse('startups:startup-detail', args=[self.startup.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Startup.objects.count(), 1)
    
    
    def test_edit_invalid_phone_number(self):
        '''
        Test editing a startup with an invalid phone number
        '''        
        new_phone = '+1234'  # no valid number
        data = {'startup_phone': new_phone}
        response = self.client.put(reverse('startups:startup-detail', args=[self.startup.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.startup.refresh_from_db()
        self.assertNotEqual(self.startup.startup_phone, new_phone)
        self.assertEqual(Startup.objects.count(), 1)


    def update_startup(self, startup_id, data):
        '''
        Helper function to update a startup
        '''
        url = reverse('startups:startup-detail', kwargs={'pk': startup_id})
        return self.client.put(url, data, format='json')


    def test_update_startup(self):
        '''
        Test updating a startup
        '''
        updated_startup_data = {
            'startup_name': 'UpdatedStartup2',
            'startup_industry': 'Finance',
            'startup_phone': '+380987654321',
            'startup_country': 'UA',
            'startup_city': 'London',
            'startup_address': '456 High St'
        }
        response = self.update_startup(self.startup.pk, updated_startup_data)

        try:
            self.startup.refresh_from_db()
        except ObjectDoesNotExist:
            self.fail("The startup object no longer exists.")
        except Exception as e:
            self.fail(f"An error occurred when refreshing the object from the database: {e}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.startup.startup_name, 'UpdatedStartup2')
        self.assertEqual(Startup.objects.count(), 1)

    def test_edit_startup_industry(self):
        '''
        Test editing the industry of a startup
        '''
        new_industry = 'ABCD'
        updated_data = {
            'startup_name': self.startup.startup_name,
            'startup_industry': new_industry,
            'startup_phone': self.startup.startup_phone,
            'startup_country': 'UA',
            'startup_city': self.startup.startup_city,
            'startup_address': self.startup.startup_address
        }
        response = self.update_startup(self.startup.id, updated_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            self.startup.refresh_from_db()
        except ObjectDoesNotExist:
            self.fail("The startup object no longer exists.")
        except Exception as e:
            self.fail(f"An error occurred when refreshing the object from the database: {e}")

        self.assertEqual(self.startup.startup_industry, new_industry)
        self.assertEqual(Startup.objects.count(), 1)

    def test_edit_startup_name(self):
        '''
        Test editing the name of a startup
        '''
        new_name = 'Abcdeer'
        updated_data = {
            'startup_name': new_name,
            'startup_industry': self.startup.startup_industry,
            'startup_phone': self.startup.startup_phone,
            'startup_country': 'UA',
            'startup_city': self.startup.startup_city,
            'startup_address': self.startup.startup_address
        }
        response = self.update_startup(self.startup.id, updated_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            self.startup.refresh_from_db()
        except ObjectDoesNotExist:
            self.fail("The startup object no longer exists.")
        except Exception as e:
            self.fail(f"An error occurred when refreshing the object from the database: {e}")

        self.assertEqual(self.startup.startup_name, new_name)
        self.assertEqual(Startup.objects.count(), 1)
    

    def test_delete_startup(self):
        '''
        Test deleting a startup
        '''
        # Checking startup deletion
        response = self.client.delete(reverse('startups:startup-detail', args=[self.startup.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Startup.objects.filter(id=self.startup.id).exists())
        self.assertEqual(Startup.objects.count(), 0)
        

    def test_update_nonexistent_startup(self):
        '''
        Test Updating Non-existent Startup
        '''
        nonexistent_id = 9999  # This ID doesn't exist in the database
        url = reverse('startups:startup-detail', args=[nonexistent_id])
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_nonexistent_startup(self):
        '''
        Test Deleting Non-existent Startup
        '''
        nonexistent_id = 9999  # This ID doesn't exist in the database
        url = reverse('startups:startup-detail', args=[nonexistent_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_invalid_data_format(self):
        '''
        Test Providing Invalid Data Format
        '''
        url = reverse('startups:startup-detail', args=[self.startup.id])
        invalid_data = {
            'startup_name': 123,  
            'startup_industry': 'Finance',
            'startup_country': 'AAA',
        }
        response = self.client.put(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        


    def test_delete_startup(self):
        '''
        Test Deleting Startup
        '''
        url = reverse('startups:startup-detail', args=[self.startup.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Startup.objects.count(), 0)


    def test_empty_data(self):
        '''
        Test Providing Empty Data
        '''
        url = reverse('startups:startup-detail', args=[self.startup.id])
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_malformed_data(self):
        '''
        Test Providing Malformed Data
        '''
        url = reverse('startups:startup-detail', args=[self.startup.id])
        malformed_data = {'startup_name': 123}  
        response = self.client.put(url, malformed_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
