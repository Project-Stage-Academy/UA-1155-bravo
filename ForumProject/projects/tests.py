from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.db import transaction
import copy
from users.models import UserRoleCompany, CustomUser, UserStartup, UserInvestor
from startups.models import Startup
from investors.models import Investor
from .models import Project, InvestorProject


class ProjectsTestCase(TestCase):
    """
    Test case class for testing project-related functionality.

    This class provides test cases for creating, updating, viewing, and deleting projects,
    as well as for following and subscribing to projects.
    """
    
    @staticmethod
    def visit_endpoint(url_name, token, method='POST', data={}, kwargs=None):
        """
        Helper function to make requests to API endpoints.

        Args:
            url_name (str): The name of the URL pattern for the endpoint.
            token (str): The JWT token for authentication.
            method (str): The HTTP method for the request (default is 'POST').
            data (dict): The request data (default is an empty dictionary).
            kwargs (dict): Dictionary for kwargs that includes, but may be not limited to,
                      the primary key of the object (default is None).

        Returns:
            Response: The response object returned by the API.
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        if method.upper() == 'GET':
            return client.get(reverse(url_name, kwargs={'pk': kwargs}), data, format='json')
        elif method.upper() == 'PUT':
            return client.put(reverse(url_name, kwargs={'pk': kwargs}), data, format='json')
        elif method.upper() == 'DELETE':
            return client.delete(reverse(url_name, kwargs=kwargs) if kwargs else 
                                 reverse(url_name), data, format='json')
        else:
            return client.post(reverse(url_name, kwargs=kwargs) if kwargs else 
                               reverse(url_name), data, format='json')
        
    @classmethod
    def follow_or_subscribe(self, token_owner, pk, action='follow'):
        """
        Helper function to follow, unfollow from, or subscribe to, a project.

        Args:
            token_owner (CustomUser): The user token owner.
            pk (dict): Dictionary for kwargs of self.visit_endpoint function.
            action (str): The action to perform ('follow', 'subscribe' or 'delist_project').

        Returns:
            Response: The response object returned by the API.
        """
        return self.visit_endpoint(
            f'projects:{action}',
            self.tokens[token_owner.email],
            'POST',
            kwargs = pk
        )
    
    @staticmethod
    def alien_user():
        """
        Helper function to create an alien user for testing purposes.

        Returns:
            CustomUser: The created user object.
        """
        return CustomUser.objects.create_user(
            email='user_alien@user.com',
            first_name='User',
            last_name='Alien',
            phone_number='+3806669966',
            password='-Qwerty-3',
            is_active=True
        )
    
    @classmethod
    @transaction.atomic
    def setUpTestData(cls):
        """
        Sets up test data for the project-related test cases.

        This method creates necessary user objects and initializes test data
        such as startup, investor, and project objects.
        """
        cls.tokens = {}

        # Create a user who will represent Startup and have him logged in
        cls.user_startuper = CustomUser.objects.create_user(
            email='startuper@user.com',
            first_name='John',
            last_name='Doe',
            phone_number='+3801234567890',
            password='-Qwerty-1',
            is_active=True
        )
        refresh = RefreshToken.for_user(cls.user_startuper)
        cls.tokens[cls.user_startuper.email] = str(refresh.access_token)
        
        # Assign role to user_startuper, create a Startup and select it for the esuer_startuper
        startuper_role = UserRoleCompany.objects.create(user=cls.user_startuper, role='startup')
        cls.startup_test = Startup.objects.create(
            startup_name = 'Python online',
            startup_industry = 'IT',
            startup_phone = '+380987654321',
            startup_country = 'UA',
            startup_city = 'Lviv',
            startup_address = 'Sirka 56'
        )
        UserStartup.objects.create(customuser=cls.user_startuper, startup=cls.startup_test, startup_role_id=1)
        startuper_role.company_id = cls.startup_test.pk
        startuper_role.save()
        
        # Create a user who will represent InvestCo and have him logged in
        cls.user_investor = CustomUser.objects.create_user(
            email='investor@user.com',
            first_name='Jane',
            last_name='Doe',
            phone_number='+380445554433',
            password='-Qwerty-2',
            is_active=True
        )
        refresh = RefreshToken.for_user(cls.user_investor)
        cls.tokens[cls.user_investor.email] = str(refresh.access_token)
        
        # Assign role to user_investor, create an InvestCo and select it for the user_investor
        investor_role = UserRoleCompany.objects.create(user=cls.user_investor, role='investor')
        cls.investor_test = Investor.objects.create(
            investor_name = 'Piggy bank',
            investor_industry = 'IT',
            investor_phone = '+380448889900',
            investor_country = 'UA',
            investor_city = 'Odessa',
            investor_address = 'Stusya 11'
        )
        UserInvestor.objects.create(customuser=cls.user_investor, investor=cls.investor_test, investor_role_id=1)
        investor_role.company_id = cls.investor_test.pk
        investor_role.save()

        # create a Project that belongs to startup_test
        cls.project_test_data = {
            'name': 'Django Forum Project',
            'description': 'Sandbox for Python programming beginners',
            'duration': 6.0,
            'budget_currency': 'UAH',
            'budget_amount': 9000
        }
        cls.project_create_response = cls.visit_endpoint(
            'projects:project-list', 
            cls.tokens[cls.user_startuper.email],
            data = cls.project_test_data
        )

    # Group of test regarding creation of a Project
    def test_ok_project_created_by_startuper(self):
        self.assertTrue(Project.objects.exists())
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().name, 'Django Forum Project')
        self.assertEqual(self.project_create_response.status_code, status.HTTP_201_CREATED)

    def test_fail_project_creation_by_investor(self):
        response = self.visit_endpoint(
            'projects:project-list', 
            self.tokens[self.user_investor.email],
            data = self.project_test_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', response.data['detail'])

    def test_fail_project_duplicate_name_creation(self):
        project_2_data = {
            'name': 'Django Forum Project',
            'description': 'Unique description',
            'duration': 12.0,
            'budget_currency': 'USD',
            'budget_amount': 3000
        }
        response = self.visit_endpoint(
            'projects:project-list', 
            self.tokens[self.user_startuper.email],
            data = project_2_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Project name must be unique for this Startup.', response.data[0])

    @transaction.atomic
    def test_ok_several_projects_created(self):
        for i in range(2):
            project_data = {
                'name': f'Project{[i]}',
                'description': f'Description{i}',
                'duration': 12.0 + i,
                'budget_currency': 'USD',
                'budget_amount': 3000 + i
            }
            response = self.visit_endpoint(
                'projects:project-list', 
                self.tokens[self.user_startuper.email],
                data = project_data
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 3)

    @transaction.atomic
    def test_fail_create_empty_mandatory_field(self):
        project_1_data = {
            'name': '',
            'description': 'Description'
        }
        project_2_data = {
            'name': 'Project_2',
            'description': '',
        }
        projects = [project_1_data, project_2_data]
        for project in projects:
            response = self.visit_endpoint(
                    'projects:project-list', 
                    self.tokens[self.user_startuper.email],
                    data = project
                )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), 1)

    # Group of tests regarding updates of a Project
    @transaction.atomic
    def test_ok_change_project_details(self):
        fields = ['name', 'description', 'duration', 'budget_amount']
        project = copy.deepcopy(self.project_test_data)
        project['name'] = 'Second Project'
        self.visit_endpoint(
            'projects:project-list', 
            self.tokens[self.user_startuper.email],
            data = project
        )
        self.assertEqual(Project.objects.count(), 2)
        for field in fields:
            suffix = '1' if isinstance(project[field], str) else 1
            project[field] += suffix
            response = self.visit_endpoint(
                    'projects:project-detail', 
                    self.tokens[self.user_startuper.email],
                    'PUT',
                    project,
                    kwargs = 2
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_change_project_by_not_owner(self):
        data_with_amended_description = {
            'name': 'Django Forum Project',
            'description': 'Amended description',
            'duration': 6.0,
            'budget_currency': 'UAH',
            'budget_amount': 9000
        }
        response = self.visit_endpoint(
                    'projects:project-detail', 
                    self.tokens[self.user_investor.email],
                    'PUT',
                    data_with_amended_description,
                    kwargs = self.project_create_response.data['id']
                )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Group of tests regarding viewing a Project
    def test_ok_ivestor_access(self):
        response = self.visit_endpoint(
            'projects:project-detail', 
            self.tokens[self.user_investor.email],
            'GET',
            kwargs = self.project_create_response.data['id']
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ok_owner_access(self):
        response = self.visit_endpoint(
            'projects:project-detail', 
            self.tokens[self.user_startuper.email],
            'GET',
            kwargs = self.project_create_response.data['id']
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_stranger_user_access(self):
        user_alien = self.alien_user()
        token = ''
        for i in range(3):
            if i == 1:
                refresh = RefreshToken.for_user(user_alien)
                token = str(refresh.access_token)
            if i == 2:
                UserRoleCompany.objects.create(user=user_alien, role='startup')
            response = self.visit_endpoint('projects:project-detail', token, 'GET', kwargs=1)
            if i:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Group of tests regarding Project deletion
    @transaction.atomic
    def test_ok_owner_deletion(self):
        local_project_data = copy.deepcopy(self.project_test_data)
        local_project_data['name'] = 'Different name'
        local_project = self.visit_endpoint(
            'projects:project-list', 
            self.tokens[self.user_startuper.email],
            data = local_project_data
        )
        self.assertEqual(Project.objects.count(), 2)
        self.assertTrue(Project.objects.get(name=local_project.data['name']))
        deletion_response = self.visit_endpoint(
            'projects:project-detail', 
            self.tokens[self.user_startuper.email],
            'DELETE',
            kwargs = {'pk': local_project.data['id']}
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertFalse(Project.objects.filter(name=local_project_data['name']))
        self.assertEqual(deletion_response.status_code, status.HTTP_200_OK)

    def test_fail_non_owner_deletion(self):
        deletion_response = self.visit_endpoint(
            'projects:project-detail', 
            self.tokens[self.user_investor.email],
            'DELETE',
            kwargs = {'pk': self.startup_test.pk}
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(deletion_response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_fail_attempt_delete_nonexisting_project(self):
        deletion_response = self.visit_endpoint(
            'projects:project-detail', 
            self.tokens[self.user_startuper.email],
            'DELETE',
            kwargs = {'pk': 1000}
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(deletion_response.status_code, status.HTTP_404_NOT_FOUND)

    # Group of tests regarding following / subscribing for Project
    def test_ok_investor_starts_follow(self):
        followed_projects = InvestorProject.objects.count()
        response = self.follow_or_subscribe(self.user_investor, {'project_id': self.project_create_response.data['id']})
        newly_followed_count = InvestorProject.objects.count() - followed_projects
        self.assertEqual(newly_followed_count, 1)
        self.assertTrue(InvestorProject.objects.filter(project=Project.objects.get(pk=self.project_create_response.data['id'])))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_attempt_to_follow_already_followed(self):
        followed_projects = InvestorProject.objects.count()
        response = self.follow_or_subscribe(self.user_investor, {'project_id': self.project_create_response.data['id']})
        newly_followed_count = InvestorProject.objects.count() - followed_projects
        self.assertEqual(newly_followed_count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.follow_or_subscribe(self.user_investor, {'project_id': self.project_create_response.data['id']})
        newly_followed_count = InvestorProject.objects.count() - followed_projects
        self.assertEqual(newly_followed_count, 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Project is already followed by this investor')

    def test_ok_investor_subscribes(self):
        share = 35
        response = self.follow_or_subscribe(
            self.user_investor, 
                {'project_id': self.project_create_response.data['id'], 'share': share},
                'subscription'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], f'Project subscribed with share {share}.')

    def test_ok_investor_stops_follow(self):
        initial_follow_count = InvestorProject.objects.count()
        self.follow_or_subscribe(self.user_investor, {'project_id': self.project_create_response.data['id']})
        response = self.follow_or_subscribe(
            self.user_investor, 
            {'project_id': self.project_create_response.data['id']}, 
            'delist_project'
        )
        final_follow_count = InvestorProject.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(initial_follow_count, final_follow_count)

    def test_fail_investor_follow_nonexisting_project(self):
        response = self.follow_or_subscribe(self.user_investor, {'project_id': 1000})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_investor_stops_follow_nonfollowed_project(self):
        self.assertTrue(Project.objects.get(pk=self.project_create_response.data['id']))
        self.assertFalse(InvestorProject.objects.filter(project=Project.objects.get(pk=self.project_create_response.data['id'])))
        response = self.follow_or_subscribe(
            self.user_investor, 
            {'project_id': self.project_create_response.data['id']}, 
            'delist_project'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_fail_noninvestor_starting_follow(self):
        response = self.follow_or_subscribe(
            self.user_startuper, 
            {'project_id': self.project_create_response.data['id']}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fail_noninvestor_subscribing(self):
        response = self.follow_or_subscribe(
            self.user_startuper, 
            {'project_id': self.project_create_response.data['id'], 'share': 15},
            'subscription'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    # Group of tests viewing Project Logs
    def test_ok_owner_views_logs(self):
        response = self.visit_endpoint(
            'projects:view_logs', 
            self.tokens[self.user_startuper.email],
            'GET',
            kwargs = self.project_create_response.data['id']
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_nonowner_viewing_logs(self):
        response = self.visit_endpoint(
            'projects:view_logs', 
            self.tokens[self.user_investor.email],
            'GET',
            kwargs = self.project_create_response.data['id']
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)