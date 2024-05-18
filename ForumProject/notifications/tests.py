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

    def test_follow_project_creates_notification(self):
        """
        Test case to check if following a project creates a notification.
        """
        # Authenticate the user with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[1]}@user.com'])

        # Get endpoint to follow a project
        self.url = reverse('projects:follow', kwargs={'project_id': self.project.id})

        # Send a POST request to follow the project
        response = self.client.post(self.url)

        # Check if the request was successful (HTTP 201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('follower(s) list changed')
        self.assertEqual(notifications_count, 1)

    def test_unfollow_project_creates_notification(self):
        """
        Test case to check if unfollowing a project creates a notification.
        """
        # Authenticate the user with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[1]}@user.com'])

        # Follow the project first to ensure there's something to unfollow
        follow_url = reverse('projects:follow', kwargs={'project_id': self.project.id})
        self.client.post(follow_url)

        # Get endpoint to unfollow a project
        unfollow_url = reverse('projects:delist_project', kwargs={'project_id': self.project.id})

        # Send a POST request to unfollow the project
        response = self.client.post(unfollow_url)

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('follower(s) list changed')
        self.assertEqual(notifications_count, 2)

    def test_subscription_creates_notification(self):
        """
        Test case to check if offering a stake in the project creates a notification.
        """
        # Authenticate the investor
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[1]}@user.com'])

        # Offer a stake in the project
        share = 50  # You can set any share value for testing purposes
        url = reverse('projects:subscription', kwargs={'project_id': self.project.id, 'share': share})
        response = self.client.post(url)

        # Check if the request was successful (HTTP 201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if a record is added to the Notification table
        notifications_count = self.get_notification_count('subscription changed')

        self.assertEqual(notifications_count, 1)

    def test_turn_off_email_notifications(self):
        """
        Test turning off email notifications.
        """
        # Authenticate the user with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[0]}@user.com'])

        url = reverse('notifications:notification_detail')
        data = {
            'email_on_followers_change': False,
            'email_on_share_subscription': False,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['email_on_followers_change'])
        self.assertFalse(response.data['email_on_share_subscription'])

    def test_turn_off_in_app_notifications(self):
        """
        Test turning off in-app notifications.
        """
        # Authenticate the user with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[0]}@user.com'])

        url = reverse('notifications:notification_detail')
        data = {
            'in_app_on_followers_change': False,
            'in_app_on_share_subscription': False,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['in_app_on_followers_change'])
        self.assertFalse(response.data['in_app_on_share_subscription'])

    def test_turn_off_all_notifications(self):
        """
        Test turning off all notifications.
        """
        # Authenticate the user with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[0]}@user.com'])

        url = reverse('notifications:notification_detail')
        data = {
            'email_on_followers_change': False,
            'email_on_share_subscription': False,
            'in_app_on_followers_change': False,
            'in_app_on_share_subscription': False,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['email_on_followers_change'])
        self.assertFalse(response.data['email_on_share_subscription'])
        self.assertFalse(response.data['in_app_on_followers_change'])
        self.assertFalse(response.data['in_app_on_share_subscription'])

    def test_unauthorized_user_cannot_follow_project(self):
        """
        Test case to check if an unauthorized user cannot follow a project.
        """
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[2]}@user.com'])

        # Get endpoint to follow a project
        url = reverse('projects:follow', kwargs={'project_id': self.project.id})

        # Send a POST request to follow the project without authentication
        response = self.client.post(url)

        # Check if the request was unsuccessful
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_subscribe_project(self):
        """
        Test case to check if an unauthorized user cannot subscribe a project.
        """
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tokens[f'{self.actors[2]}@user.com'])

        # Get endpoint to follow a project
        share = 50
        url = reverse('projects:subscription', kwargs={'project_id': self.project.id, 'share': share})

        # Send a POST request to follow the project without authentication
        response = self.client.post(url)

        # Check if the request was unsuccessful
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
