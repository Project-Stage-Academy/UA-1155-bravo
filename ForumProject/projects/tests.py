from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import random, string
from users.models import UserRoleCompany, CustomUser, UserStartup, UserInvestor
from startups.models import Startup
from investors.models import Investor
from projects.models import Project
from notifications.models import Notification


class ProjectsTestCase(TestCase):
    """
    TODO - make proper docstring
    """
    
    @staticmethod
    def visit_endpoint(data, url_name, token):
        """
        Helper function. TODO - make proper docstring
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client.post(reverse(url_name), data, format='json')
    
    @classmethod
    @transaction.atomic
    def setUpTestData(cls):
        """
        TODO - make proper docstring
        """
        
        # Create a user who will represent Startup
        cls.user_startuper = CustomUser.objects.create_user(
            email='startuper@user.com',
            first_name='John',
            last_name='Doe',
            phone_number='+3801234567890',
            password='-Qwerty-1',
            is_active=True
        )
        
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
        
        # Create a user who will represent InvestCo
        cls.user_investor = CustomUser.objects.create_user(
            email='investor@user.com',
            first_name='Jane',
            last_name='Doe',
            phone_number='+380445554433',
            password='-Qwerty-2',
            is_active=True
        )
        
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


