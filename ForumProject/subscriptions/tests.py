from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser, UserInvestor, UserStartup, UserRoleCompany
from investors.models import Investor
from startups.models import Startup
from notifications.models import Notification
from subscriptions.models import SubscribeInvestorStartup
from rest_framework.test import APIClient, APITestCase
from django.db import transaction
from django.utils import timezone


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
        
        cls.investor_user2 = CustomUser.objects.create_user(
            email='investor2@example.com',
            first_name='Investor2',
            last_name='User2',
            phone_number='+3801234562',
            password='password2',
            is_active=True
        )

        refresh_investor = RefreshToken.for_user(cls.investor_user2)
        cls.investor_token2 = str(refresh_investor.access_token)

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
        
        # Set up credentials for the investor user2
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token2)
        
        # Create investor profile
        self.investor_profile2 = Investor.objects.create(
            investor_name='Test Investor2',
            investor_industry='IT',
            investor_phone='+3801234567',
            investor_country='UA',
            investor_city='Test City2',
            investor_address='Test Address2'
        )
        
        # Associate investor profile with investor user and assign role
        UserInvestor.objects.create(customuser=self.investor_user2, investor=self.investor_profile2, investor_role_id=1)
        UserRoleCompany.objects.create(user=self.investor_user2, role='investor', company_id=self.investor_profile2.id)
        
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
        SubscribeInvestorStartup.objects.all().delete()


    def test_user_investor_has_role(self):
        """
        Test if the user with the role of investor, investor2, startup  has a role assigned.

        Retrieves a user with the role of investor, investor2, startup and checks if a role is assigned to them.
        """
        user1 = CustomUser.objects.get(email='investor@example.com')
        user_role_company1 = UserRoleCompany.objects.filter(user=user1).first()
        self.assertIsNotNone(user_role_company1, "User_investor doesn't have a role.")
        
        user2 = CustomUser.objects.get(email='investor2@example.com')
        user_role_company2 = UserRoleCompany.objects.filter(user=user2).first()
        self.assertIsNotNone(user_role_company2, "User_investor2 doesn't have a role.")
        
        user3 = CustomUser.objects.get(email='startup@example.com')
        user_role_company3 = UserRoleCompany.objects.filter(user=user3).first()
        self.assertIsNotNone(user_role_company3, "User_startup doesn't have a role.")
        


    def test_user_investor_startup_role_company_relationship_exists(self):
        """
        Check if there is an entry in the UserRoleCompany table for the investoruser, investoruser2, startupuser.
        """
        user_role_company_relationship_exists1 = UserRoleCompany.objects.filter(user=self.investor_user, role='investor', company_id=self.investor_profile.id).exists()
        self.assertTrue(user_role_company_relationship_exists1, "UserRoleCompany1 relationship does not exist.")

        user_role_company_relationship_exists2 = UserRoleCompany.objects.filter(user=self.investor_user2, role='investor', company_id=self.investor_profile2.id).exists()
        self.assertTrue(user_role_company_relationship_exists2, "UserRoleCompany2 relationship does not exist.")
        
        user_role_company_relationship_exists3 = UserRoleCompany.objects.filter(user=self.startup_user, role='startup', company_id=self.startup_profile.id).exists()
        self.assertTrue(user_role_company_relationship_exists3, "UserRoleCompany3 relationship does not exist.")

  
    def test_user_investor_relationship_Table_UserInvestor_exists(self):
        """
        Checking if an entry exists in the UserInvestor, UserStartup table for the investor user, investor user2, startup user.
        """
        user_investor_relationship_exists1 = UserInvestor.objects.filter(customuser=self.investor_user, investor=self.investor_profile).exists()
        self.assertTrue(user_investor_relationship_exists1, "User-Investor relationship does not exist.")
        
        user_investor_relationship_exists2 = UserInvestor.objects.filter(customuser=self.investor_user2, investor=self.investor_profile2).exists()
        self.assertTrue(user_investor_relationship_exists2, "User-Investor2 relationship does not exist.")

        user_investor_relationship_exists3 = UserStartup.objects.filter(customuser=self.startup_user, startup=self.startup_profile).exists()
        self.assertTrue(user_investor_relationship_exists3, "User-Startup relationship does not exist.")
        
    
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

    def test_invalid_token_subscribe(self):
        """
        Test that subscribing with an invalid token results in unauthorized access.
        """
        subscribe_url = reverse('subscriptions:add-subscriptions')
        invalid_token = 'invalid_token'
        subscription_data = {'startup': self.startup_profile.id}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + invalid_token)
        response = self.client.post(subscribe_url, subscription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def create_subscription_instance(self):
        """
        Helper method to create a subscription instance.

        Returns:
            SubscribeInvestorStartup: Instance of SubscribeInvestorStartup.
        """
        return SubscribeInvestorStartup.objects.create(investor=self.investor_profile, startup=self.startup_profile)
    
    def test_view_subscription_by_id(self):
        """
        Test viewing a subscription by its ID.

        Creates a subscription instance, retrieves its ID, then sends a GET request to view the subscription
        using its ID. Checks if the response status code is 200 OK and if the subscription ID is present in the response.

        """
        subscription_instance = self.create_subscription_instance()
        subscription_id = subscription_instance.id
        
        view_subscription_url = reverse('subscriptions:subscription-detail', kwargs={'pk': subscription_id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)

        response = self.client.get(view_subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscription_id = response.data.get('id', None)
        self.assertIsNotNone(subscription_id, "Subscription ID is missing in the response.")

    def test_delete_subscription(self):
        """
        Test deleting a subscription.

        Creates a subscription instance, retrieves its ID, then sends a DELETE request to delete the subscription.
        Checks if the response status code is 204 No Content, indicating successful deletion.

        """
        subscription_instance = self.create_subscription_instance()
        subscription_id = subscription_instance.id

        delete_subscription_url = reverse('subscriptions:subscription-detail', kwargs={'pk': subscription_id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)

        response = self.client.delete(delete_subscription_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_view_not_personal_subscription(self):
        """
        Test deleting not personal subscription.
        """
        # Create a subscription with investor_profile
        SubscribeInvestorStartup.objects.create(investor=self.investor_profile, startup=self.startup_profile)
        
        # Create a subscription with investor_profile2
        subscription_instance = SubscribeInvestorStartup.objects.create(investor=self.investor_profile2, startup=self.startup_profile)
        
        # Get the ID of the subscription created by investor_profile2
        subscription_id = subscription_instance.id

        # Attempt to delete the subscription using investor_profile's token
        view_subscription_url = reverse('subscriptions:subscription-detail', kwargs={'pk': subscription_id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)

        # Send DELETE request
        response = self.client.get(view_subscription_url)

        # Check if the response status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Check if the response contains the expected error message
        self.assertEqual(response.data, {"error": "Subscription not found"}, "Incorrect error message returned")

    def test_view_non_existent_subscription(self):
        """
        Test viewing a non-existent subscription.

        Retrieves the URL for viewing a subscription with an invalid ID.
        Sets up the client with the investor token.
        Executes a GET request to view the subscription with the invalid ID.
        Checks that the response status code is 404 Not Found.
        Checks that the response contains the expected error message.
        """
        invalid_subscription_id = 9999  
        view_subscription_url = reverse('subscriptions:subscription-detail', kwargs={'pk': invalid_subscription_id})
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)

        response = self.client.get(view_subscription_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Subscription not found"})
        
    def test_no_permission_update_startup(self):
        """
        Test that an investor user does not have permission to update a startup profile.
        """
        update_url = reverse('startups:startup-detail', kwargs={'pk': self.startup_profile.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        updated_data = {
            'startup_name': 'UpdatedTestStartup',
            'startup_industry': 'Tech',
            'startup_phone': '+3809876543',
            'startup_country': 'UA',
            'startup_city': 'Test City',
            'startup_address': 'Test Address'
        }
        response = self.client.put(update_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail':'You do not have permission to perform this action.'})

    
    def create_subscription_and_update_startup(self, investor_profile, startup_profile):
        """
        Create a subscription for the given investor and startup, then update the startup profile.

        Args:
            investor_profile (Investor): The investor profile to subscribe.
            startup_profile (Startup): The startup profile to be updated.

        Returns:
            tuple: A tuple containing the response object of the startup profile update and the current time.

        Raises:
            AssertionError: If the startup profile is not updated successfully.
        """
        # Create subscription for the given investor and startup
        SubscribeInvestorStartup.objects.create(investor=investor_profile, startup=startup_profile)
        
        # Edit the startup profile
        updated_data = {
            'startup_name': 'UpdatedTestStartup',
            'startup_industry': 'Tech',
            'startup_phone': '+3809876543',
            'startup_country': 'UA',
            'startup_city': 'Test City',
            'startup_address': 'Test Address'
        }
        update_url = reverse('startups:startup-detail', kwargs={'pk': startup_profile.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)
        update_response = self.client.put(update_url, updated_data)

        # Check if the startup profile is successfully updated
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_data['startup_name'], Startup.objects.get(pk=startup_profile.pk).startup_name,
                        f"Startup name did not update properly. Expected: {updated_data['startup_name']}, "
                        f"but got: {Startup.objects.get(pk=startup_profile.pk).startup_name}")

    def tearDown(self):
        """
        Clean up the test data after each individual test.
        """
        # Clean up only after the specific test
        Notification.objects.all().delete()

    def test_profile_update_notification(self):
        """
        Test if the notification is sent to the investor when the startup profile is updated.
        """
        # Отримати відповідь на оновлення та поточний час
        self.create_subscription_and_update_startup(self.investor_profile, self.startup_profile)

        # Check if the corresponding notification is displayed in the investor's notification list
        notification_url = reverse('investors:investor-notify')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        notifications_response = self.client.get(notification_url)

        self.assertEqual(notifications_response.status_code, status.HTTP_200_OK)
        notification_count = Notification.objects.count()
        self.assertGreater(notification_count, 0, "No notifications found in the database")
        
        expected_data = {
            "project": None,
            "startup": 78,
            "investor": 39,
            "trigger": "startup profile updated",
            "initiator": "startup",
        }
        first_notification_data = notifications_response.data[0]  
        self.assertEqual(first_notification_data['project'], expected_data['project'])
        self.assertEqual(first_notification_data['startup'], expected_data['startup'])
        self.assertEqual(first_notification_data['investor'], expected_data['investor'])
        self.assertEqual(first_notification_data['trigger'], expected_data['trigger'])
        self.assertEqual(first_notification_data['initiator'], expected_data['initiator'])

    def tearDown(self):
        """
        Clean up the test data after each individual test.
        """
        # Clean up only after the specific test
        Notification.objects.all().delete()

    def test_notifications_two_investors(self):
        """
        Test if notifications are sent to multiple investors when the startup profile is updated.
        """
        self.create_subscription_and_update_startup(self.investor_profile, self.startup_profile)
        self.create_subscription_and_update_startup(self.investor_profile2, self.startup_profile)

        # Check if the corresponding notification is displayed in the investor's notification list
        notification_url = reverse('investors:investor-notify')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        notifications_response = self.client.get(notification_url)

        self.assertEqual(notifications_response.status_code, status.HTTP_200_OK)
        notification_count = Notification.objects.count()
        self.assertGreater(notification_count, 1, "No notifications found in the database")
        
        expected_data2 = {
            "project": None,
            "startup": 77,
            "investor": 37,
            "trigger": "startup profile updated",
            "initiator": "startup",
        }
        first_notification_data = notifications_response.data[1]  
        self.assertEqual(first_notification_data['project'], expected_data2['project'])
        self.assertEqual(first_notification_data['startup'], expected_data2['startup'])
        self.assertEqual(first_notification_data['investor'], expected_data2['investor'])
        self.assertEqual(first_notification_data['trigger'], expected_data2['trigger'])
        self.assertEqual(first_notification_data['initiator'], expected_data2['initiator'])


