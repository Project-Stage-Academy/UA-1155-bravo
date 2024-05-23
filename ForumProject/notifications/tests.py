from django.test import TestCase
from django.urls import reverse
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.test import APIClient
from users.models import UserRoleCompany, CustomUser, UserStartup, UserInvestor
from investors.models import Investor
from projects.models import Project
from .models import Notification
from .tests_constants import get_urls, EXPECTED_STATUS


class NotificationsTestCase(TestCase):
    """
    A TestCase class for testing notification-related functionalities.
    """

    @staticmethod
    def create_object(data, url_name, token):
        """
        Helper method to create an object via an API endpoint using the provided data.

        Args:
            data (dict): The data to be sent in the request body.
            url_name (str): The name of the URL endpoint to send the request to.
            token (str): The JWT token used for authentication.

        Returns:
            Response: The response object returned from the API endpoint.

        Example:
            data = {
                'startup_name': 'Example Startup',
                'startup_industry': 'Technology',
                'startup_phone': '+1234567890',
                'startup_country': 'US',
                'startup_city': 'New York',
                'startup_address': '123 Example St'
            }
            url_name = 'startups:startup-add'
            token = 'your_jwt_token'
            response = NotificationsTestCase.create_object(data, url_name, token)
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client.post(reverse(url_name), data, format='json')

    def get_notification_count(self, trigger):
        """
        Helper function to get the count of notifications based on trigger.
        """
        current_investor_id = UserRoleCompany.objects.get(user=self.users[1]).company_id
        current_investor = Investor.objects.get(id=current_investor_id)
        return Notification.objects.filter(
            project=self.project,
            startup=self.project.startup,
            investor=current_investor,
            trigger=trigger,
            initiator='investor'
        ).count()

    @classmethod
    @transaction.atomic
    def setUpTestData(cls):
        """
        Set up test data for the test case.
        """
        cls.actors = ['startup', 'inv_company', 'inv_lonely']
        cls.users = []
        cls.tokens = {}

        # Create three users - one with role of Startup and two with role of Investor
        for i in range(3):
            user = CustomUser.objects.create_user(
                email=f'{cls.actors[i]}@user.com',
                first_name=f'{cls.actors[i].capitalize()}',
                last_name=f'{cls.actors[i].capitalize()}',
                phone_number=f'+3801234567{i}',
                password='stupidpassword',
                is_active=True
            )

            # assign role
            role = 'startup' if not i else 'investor'
            UserRoleCompany.objects.create(user=user, role=role)

            cls.users.append(user)

            # Get JWT token for the user
            refresh = RefreshToken.for_user(user)
            cls.tokens[user.email] = str(refresh.access_token)

        # Create Startup company
        startup_data = {
            'startup_name': 'Django Dribblers',
            'startup_industry': 'IT',
            'startup_phone': '+3801234567',
            'startup_country': 'UA',
            'startup_city': 'Lviv',
            'startup_address': 'I Franka 123'
        }
        cls.create_object(
            startup_data,
            'startups:startup-add',
            cls.tokens[f'{cls.actors[0]}@user.com']
        )

        # select Startup company for the current session
        startup_role = UserRoleCompany.objects.get(user=cls.users[0])
        startup_role.company_id = UserStartup.objects.get(customuser=cls.users[0]).startup.pk
        startup_role.save()

        # create Project
        project_data = {
            'name': 'Project1',
            'status': 'open',
            'description': 'Some description',
            'duration': 1.0,
            'budget_currency': 'UAH',
            'budget_amount': 200000
        }
        project_response = cls.create_object(
            project_data,
            'projects:project-list',
            cls.tokens[f'{cls.actors[0]}@user.com']
        )
        cls.project = Project.objects.get(id=project_response.data['id'])
        cls.urls = get_urls(cls.project.id)

        # Create Investor company
        investor_data = {
            'investor_name': 'Investor',
            'investor_industry': 'IT',
            'investor_phone': '+380448885522',
            'investor_country': 'UA',
            'investor_city': 'Kyiv',
            'investor_address': 'Sirka 25'
        }
        cls.create_object(
            investor_data,
            'investors:investor-add',
            cls.tokens[f'{cls.actors[1]}@user.com']
        )

        # select Investor company for one of the investors for the current session
        investor_role = UserRoleCompany.objects.get(user=cls.users[1])
        investor_role.company_id = UserInvestor.objects.get(customuser=cls.users[1]).investor.pk
        investor_role.save()

    def setUp(self):
        """
        Setup that is executed before each test case.
        """
        self.client = APIClient()

    def authenticate(self, actor_index):
        """
        Helper method to set the credentials for a specific user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[actor_index]}@user.com'])

    def test_follow_project_creates_notification(self):
        """
        Test case to check if following a project creates a notification.
        """
        self.authenticate(1)  # Authenticate as investor company

        # Send a POST request to follow the project
        response = self.client.post(self.urls['FOLLOW_URL'])

        # Check if the request was successful (HTTP 201 Created)
        self.assertEqual(response.status_code, EXPECTED_STATUS['CREATED'])

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('Project follower list or subscription share change')
        self.assertEqual(notifications_count, 1)

    def test_unfollow_project_creates_notification(self):
        """
        Test case to check if unfollowing a project creates a notification.
        """
        self.authenticate(1)  # Authenticate as investor company

        # Follow the project first to ensure there's something to unfollow
        self.client.post(self.urls['FOLLOW_URL'])

        # Send a POST request to unfollow the project
        response = self.client.post(self.urls['UNFOLLOW_URL'])

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, EXPECTED_STATUS['OK'])

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('Project follower list or subscription share change')
        self.assertEqual(notifications_count, 2)

    def test_subscription_creates_notification(self):
        """
        Test case to check if offering a stake in the project creates a notification.
        """
        self.authenticate(1)  # Authenticate as investor company

        # Offer a stake in the project
        response = self.client.post(self.urls['SUBSCRIPTION_URL'])

        # Check if the request was successful (HTTP 201 Created)
        self.assertEqual(response.status_code, EXPECTED_STATUS['CREATED'])

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('Project follower list or subscription share change')

        self.assertEqual(notifications_count, 1)

    def test_turn_off_email_notifications(self):
        """
        Test turning off email notifications.
        """
        self.authenticate(0)  # Authenticate as startup

        data = {
            'email_project_on_investor_interest_change': False
        }
        response = self.client.put(self.urls['NOTIFICATION_DETAIL_URL'], data, format='json')
        self.assertEqual(response.status_code, EXPECTED_STATUS['OK'])
        self.assertFalse(response.data['email_project_on_investor_interest_change'])

    def test_turn_off_in_app_notifications(self):
        """
        Test turning off in-app notifications.
        """
        self.authenticate(0)  # Authenticate as startup

        data = {
            'push_project_on_investor_interest_change': False
        }
        response = self.client.put(self.urls['NOTIFICATION_DETAIL_URL'], data, format='json')
        self.assertEqual(response.status_code, EXPECTED_STATUS['OK'])
        self.assertFalse(response.data['push_project_on_investor_interest_change'])

    def test_turn_off_all_notifications(self):
        """
        Test turning off all notifications.
        """
        self.authenticate(0)  # Authenticate as startup

        data = {
            'email_project_on_investor_interest_change': False,
            'push_project_on_investor_interest_change': False
        }
        response = self.client.put(self.urls['NOTIFICATION_DETAIL_URL'], data, format='json')
        self.assertEqual(response.status_code, EXPECTED_STATUS['OK'])
        self.assertFalse(response.data['email_project_on_investor_interest_change'])
        self.assertFalse(response.data['push_project_on_investor_interest_change'])

    def test_unauthorized_user_cannot_follow_project(self):
        """
        Test case to check if an unauthorized user cannot follow a project.
        """
        self.authenticate(2)  # Non-login user

        # Send a POST request to follow the project without authentication
        response = self.client.post(self.urls['FOLLOW_URL'])

        # Check if the request was unsuccessful
        self.assertEqual(response.status_code, EXPECTED_STATUS['FORBIDDEN'])

    def test_unauthorized_user_cannot_subscribe_project(self):
        """
        Test case to check if an unauthorized user cannot subscribe a project.
        """
        self.authenticate(2)  # Non-login user

        # Send a POST request to follow the project without authentication
        response = self.client.post(self.urls['SUBSCRIPTION_URL'])

        # Check if the request was unsuccessful
        self.assertEqual(response.status_code, EXPECTED_STATUS['FORBIDDEN'])
