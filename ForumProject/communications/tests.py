import asyncio

from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client
from django.urls import reverse

from communications.consumers import ChatConsumer
from communications.models import Room
from communications.utils import get_room, get_user_first_name
from investors.models import Investor
from startups.models import Startup
from users.models import CustomUser, UserStartup, UserRoleCompany, UserInvestor


class CommunicationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a CustomUser for authentication
        cls.startup_user = CustomUser.objects.create_user(
            email='startup@example.com',
            first_name='John',
            last_name='Doe',
            phone_number='+3801234567',
            password='password',
            is_active=True
        )

        cls.investor_user = CustomUser.objects.create_user(
            email='investor@example.com',
            first_name='Investor',
            last_name='User',
            phone_number='+3801234567',
            password='password',
            is_active=True
        )

    def setUp(self):
        '''
        Setup that is executed before each test case.
        '''
        self.client = Client()

        # Sample data for testing
        self.startup = Startup.objects.create(startup_name='Django startups',
                                              startup_industry='IT',
                                              startup_phone='+3801234567',
                                              startup_country='UA',
                                              startup_city='Lviv',
                                              startup_address='I Franka 123')

        UserStartup.objects.create(customuser=self.startup_user, startup=self.startup, startup_role_id=1)
        UserRoleCompany.objects.create(user=self.startup_user, role='startup', company_id=self.startup.id)

        # Sample data for testing
        self.startup_data = {
            'startup_name': 'Django Dribblers',
            'startup_industry': 'IT',
            'startup_phone': '+3801234562',
            'startup_country': 'UA',
            'startup_city': 'Lviv',
            'startup_address': 'I Franka 123'
        }

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
        Room.objects.all().delete()

    def test_view_chats(self):
        login = self.client.login(email='investor@example.com', password='password')
        response = self.client.get(reverse('communications:chat-index'))
        self.assertEqual(response.status_code, 200)

    def test_login_required_chats(self):
        response = self.client.get(reverse('communications:chat-index'))
        self.assertEqual(response.status_code, 302)

    def test_investor_starts_chat(self):
        login = self.client.login(email='investor@example.com', password='password')
        response = self.client.get(reverse('communications:chat-room', kwargs={'user_id': self.startup_user.id}))
        self.assertEqual(response.status_code, 200)

    def test_startup_starts_chat(self):
        login = self.client.login(email='startup@example.com', password='password')
        response = self.client.get(reverse('communications:chat-room', kwargs={'user_id': self.investor_user.id}))
        self.assertEqual(response.status_code, 403)

    def test_startup_answer_chat(self):
        login_investor = self.client.login(email='investor@example.com', password='password')
        create_chat = self.client.get(reverse('communications:chat-room', kwargs={'user_id': self.startup_user.id}))
        login = self.client.login(email='startup@example.com', password='password')
        response = self.client.get(reverse('communications:chat-room', kwargs={'user_id': self.investor_user.id}))
        self.assertEqual(response.status_code, 200)


class ChatConsumerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='chat_user@example.com',
            first_name='John',
            last_name='Doe',
            phone_number='+3801234567',
            password='password',
            is_active=True
        )
        self.room = Room.objects.create(name='chat_2_1')
        self.client.login(email='chat_user@example.com', password='password')

    async def connect_to_chat(self, user):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/chat/chat_2_1/")
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {'kwargs': {'room_name': 'chat_2_1'}}
        connected, subprotocol = await communicator.connect()
        return communicator, connected

    async def test_connect_authenticated_user(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'user_list')
        await communicator.disconnect()

    async def test_connect_unauthenticated_user(self):
        communicator, connected = await self.connect_to_chat(AnonymousUser())
        self.assertFalse(connected)

    async def test_receive_message(self):
        communicator, connected = await self.connect_to_chat(self.user)

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'user_list')

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'user_join')

        message = {'message': 'Hello, world!'}
        await communicator.send_json_to(message)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f'chat_2_1',
            {
                'type': 'chat_message',
                'user': await get_user_first_name(self.user),
                'message': message['message'],
            }
        )

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'chat_message')
        self.assertEqual(response['message'], 'Hello, world!')

        await communicator.disconnect()


