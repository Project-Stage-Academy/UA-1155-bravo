from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser, UserInvestor, UserStartup, UserRoleCompany
from investors.models import Investor
from startups.models import Startup
from subscriptions.models import SubscribeInvestorStartup
from rest_framework.test import APIClient, APITestCase


class SubscriptionTests(APITestCase):
    """
    Tests for subscribing an investor to a startup.

    This test case class contains tests related to the subscription process, such as subscribing an investor
    to a startup.

    Attributes:
        investor_user (CustomUser): User instance representing an investor.
        investor_token (str): Access token for the investor user.
        startup_user (CustomUser): User instance representing a startup.
        startup_token (str): Access token for the startup user.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the test case.

        Creates test users for an investor and a startup, along with their access tokens.

        """
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

        cls.startup_user = CustomUser.objects.create_user(
            email='startup@example.com',
            first_name='Startup',
            last_name='User',
            phone_number='+3809876543',
            password='password',
            is_active=True
        )

        refresh_startup = RefreshToken.for_user(cls.startup_user)
        cls.startup_token = str(refresh_startup.access_token)

    def setUp(self):
        '''
        Setup that is executed before each test case.
        '''

        self.client = APIClient()
        # Set up credentials for the investor user
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        
        # Create investor profile
        self.investor_profile = Investor.objects.create(
            investor_name='Test Investor',
            investor_industry='IT',
            investor_phone='+3801234567',
            investor_country='UA',
            investor_city='Test City',
            investor_address='Test Address'
        )
        
        # Associate investor profile with investor user and assign role
        UserInvestor.objects.create(customuser=self.investor_user, investor=self.investor_profile, investor_role_id=1)
        UserRoleCompany.objects.create(user=self.investor_user, role='investor', company_id=self.investor_profile.id)
        
        # Switch credentials to the startup user
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)

        # Create startup profile
        self.startup_profile = Startup.objects.create(
            startup_name='Test Startup',
            startup_industry='Tech',
            startup_phone='+3809876543',
            startup_country='UA',
            startup_city='Test City',
            startup_address='Test Address'
        )
        
        # Associate startup profile with startup user and assign role
        UserStartup.objects.create(customuser=self.startup_user, startup=self.startup_profile, startup_role_id=1)
        UserRoleCompany.objects.create(user=self.startup_user, role='startup', company_id=self.startup_profile.id)

    def test_user_investor_has_role(self):
        """
        Test if the user with the role of investor has a role assigned.

        Retrieves a user with the role of investor and checks if a role is assigned to them.
        """
        user = CustomUser.objects.get(email='investor@example.com')
        user_role_company = UserRoleCompany.objects.filter(user=user).first()
        self.assertIsNotNone(user_role_company, "User_investor doesn't have a role.")
        
    def test_user_startup_has_role(self):
        """
        Test if the user with the role of startup has a role assigned.

        Retrieves a user with the role of startup and checks if a role is assigned to them.
        """
        user = CustomUser.objects.get(email='startup@example.com')
        user_role_company = UserRoleCompany.objects.filter(user=user).first()
        self.assertIsNotNone(user_role_company, "User_startup doesn't have a role.")

    def test_user_investor_role_company_relationship_exists(self):
        """
        Check if there is an entry in the UserRoleCompany table for the investor user
        """
        user_role_company_relationship_exists = UserRoleCompany.objects.filter(user=self.investor_user, role='investor', company_id=self.investor_profile.id).exists()
        self.assertTrue(user_role_company_relationship_exists, "UserRoleCompany relationship does not exist.")

    def test_user_startup_role_company_relationship_exists(self):
        """
        Check if there is an entry in the UserRoleCompany table for the startup user
        """
        user_role_company_relationship_exists = UserRoleCompany.objects.filter(user=self.startup_user, role='startup', company_id=self.startup_profile.id).exists()
        self.assertTrue(user_role_company_relationship_exists, "UserRoleCompany relationship does not exist.")
        
    def test_user_investor_relationship_Table_UserInvestor_exists(self):
        """
        Checking if an entry exists in the UserInvestor table for the investor user
        """
        user_investor_relationship_exists = UserInvestor.objects.filter(customuser=self.investor_user, investor=self.investor_profile).exists()
        self.assertTrue(user_investor_relationship_exists, "User-Investor relationship does not exist.")
        
    def test_user_startup_relationship_Table_UserStartup_exists(self):
        """
        Checking if an entry exists in the UserStartup table for the startup user
        """
        user_investor_relationship_exists = UserStartup.objects.filter(customuser=self.startup_user, startup=self.startup_profile).exists()
        self.assertTrue(user_investor_relationship_exists, "User-Startup relationship does not exist.")

    
    def create_subscription(self, investor_token, startup_id):
        """
        Helper method to create a subscription for a user.

        Args:
            investor_token (str): User token for authentication.
            startup_id (int): ID of the startup for subscription.

        Returns:
            Response: Response object from the POST request to create a subscription.
        """
        subscribe_url = reverse('subscriptions:add-subscriptions')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + investor_token)
        subscription_data = {'startup': startup_id}
        return self.client.post(subscribe_url, subscription_data, format='json')

    def test_subscribe_investor_to_startup(self):
        """
        Test subscribing an investor to a startup.
        """
        response = self.create_subscription(self.investor_token, self.startup_profile.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SubscribeInvestorStartup.objects.filter(
            investor=self.investor_profile,
            startup=self.startup_profile
        ).exists())

    def test_duplicate_subscription(self):
        """
        Test attempting to subscribe to the same startup twice.
        """
        response = self.create_subscription(self.investor_token, self.startup_profile.id)
        response = self.create_subscription(self.investor_token, self.startup_profile.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Subscription already exists'})

    def test_subscription_list_endpoint(self):
        """
        Test whether a subscription exists at the 'subscriptions/my/' endpoint.
        """
        self.create_subscription(self.investor_token, self.startup_profile.id)
        subscription_list_url = reverse('subscriptions:my-subscriptions')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(subscription_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)
     
        