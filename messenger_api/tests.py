from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from messenger.models import Chat, Message
from messenger_api.serializers import UserListSerializer, ChatSerializer, MessageSerializer


class APITests(APITestCase):

    def setUp(self):
        self.credentials = {
            'username': 'test_user',
            'password': 'secret_password'
        }
        self.test_user1 = User.objects.create_user(**self.credentials)
        self.test_user2 = User.objects.create_user(username='test_user2', password='secret_password')
        self.test_user3 = User.objects.create_user(username='test_user3', password='secret_password')
        self.test_user5 = User.objects.create_user(username='test_user5', password='secret_password')

        self.chat_1 = Chat.objects.create()
        self.test_user1.chat_set.add(self.chat_1)
        self.test_user2.chat_set.add(self.chat_1)
        for i in range(25):
            Message.objects.create(author=self.test_user1, message=f'hello{i}', chat=self.chat_1)

        self.chat_2 = Chat.objects.create()
        self.test_user1.chat_set.add(self.chat_2)
        self.test_user3.chat_set.add(self.chat_2)
        Message.objects.create(author=self.test_user1, message='hello', chat=self.chat_2)

        self.chat_3 = Chat.objects.create()
        self.test_user2.chat_set.add(self.chat_3)
        self.test_user3.chat_set.add(self.chat_3)

    @override_settings(DEBUG=False)
    def test_registration_create_user(self):
        """
        Ensure API registration works with valid data
        """
        valid_credentials = {
            'username': 'test_user4',
            'email': 'test@test.ru',
            'password1': 'secret_password',
            'password2': 'secret_password'
        }
        response = self.client.post(reverse('api_register'), valid_credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(username='test_user4'))

    @override_settings(DEBUG=False)
    def test_registration_create_invalid_user_failed(self):
        """
        Ensure API registration does not work with invalid data
        """
        invalid_credentials = {
            'username': 'test_user4',
            'email': 'testtest',
            'password1': 'secret_password',
            'password2': 'secret'
        }
        response = self.client.post(reverse('api_register'), invalid_credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(ObjectDoesNotExist, User.objects.get, username='test_user4')

    @override_settings(DEBUG=False)
    def test_get_friend_users(self):
        """
        Ensure we can get list of friends of user
        """
        url = reverse('user-list')
        response_unauthorized = self.client.get(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        serializer_data = UserListSerializer([self.test_user2, self.test_user3], many=True).data
        self.assertEqual(serializer_data, response.data["results"])

    @override_settings(DEBUG=False)
    def test_get_detail_friend_users(self):
        """
        Ensure we can get detail of friend of user
        """
        url = reverse('user-detail', args=['test_user2'])
        response_unauthorized = self.client.get(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(url)
        serializer_data = UserListSerializer(self.test_user2).data
        self.assertEqual(serializer_data, response.data)

    @override_settings(DEBUG=False)
    def test_get_list_of_chats(self):
        """
        Ensure we can get list of chats of user
        """
        url = reverse('chat-list')
        response_unauthorized = self.client.get(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(url)
        serializer_data = ChatSerializer([self.chat_1, self.chat_2], many=True).data
        self.assertEqual(serializer_data, response.data["results"])

    @override_settings(DEBUG=False)
    def test_get_detail_chat(self):
        """
        Ensure we can get list of messages in specified chat
        """
        url = reverse('chat-detail', args=['1'])
        response_unauthorized = self.client.get(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token_test_user5 = Token.objects.get(user__username='test_user5')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_test_user5.key)
        response_authorized_another_user = self.client.get(url)
        self.assertEqual(response_authorized_another_user.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        self.assertEqual(response.data["count"], 25)

    @override_settings(DEBUG=False)
    def test_delete_chat(self):
        """
        Ensure we can delete specified chat
        """
        url = reverse('chat-detail', args=['1'])
        response_unauthorized = self.client.delete(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token_test_user5 = Token.objects.get(user__username='test_user5')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_test_user5.key)
        response_authorized_another_user = self.client.delete(url)
        self.assertEqual(response_authorized_another_user.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.delete(url)
        self.assertEqual(str(response.data), "{'success': 'chat deleted'}")
        self.assertNotIn(self.chat_1, self.test_user1.chat_set.all())

    @override_settings(DEBUG=False)
    def test_create_chat(self):
        """
        Ensure we can create chat with valid credentials
        """
        url = reverse('chat-list')
        valid_credentials = {
            'member': 'test_user5',
        }
        response_unauthorized = self.client.post(url, valid_credentials, follow=True)
        self.assertEqual(response_unauthorized.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.post(url, valid_credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Chat.objects.filter(member__username='test_user').filter(member__username='test_user5'))

    @override_settings(DEBUG=False)
    def test_create_invalid_chat_fails(self):
        """
        Ensure we can't create chat with invalid credentials
        """
        invalid_credentials = {
            'member': 'noname',
        }
        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(reverse('chat-list'), invalid_credentials, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Chat.objects.filter(member__username='test_user').filter(member__username='noname'))

    @override_settings(DEBUG=False)
    def test_get_detail_message(self):
        """
        Ensure we can get detailed message
        """
        url = reverse('message-detail', args=['1'])
        response_unauthorized = self.client.get(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token_test_user5 = Token.objects.get(user__username='test_user5')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_test_user5.key)
        response_authorized_another_user = self.client.get(url)
        self.assertEqual(response_authorized_another_user.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        serializer_data = MessageSerializer(Message.objects.get(pk=1)).data
        self.assertEqual(response.data, serializer_data)

    @override_settings(DEBUG=False)
    def test_delete_message(self):
        """
        Ensure we can delete message
        """
        url = reverse('message-detail', args=['1'])
        response_unauthorized = self.client.delete(url)
        self.assertEqual(response_unauthorized.status_code, 403)

        token_test_user5 = Token.objects.get(user__username='test_user5')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_test_user5.key)
        response_authorized_another_user = self.client.delete(url)
        self.assertEqual(response_authorized_another_user.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.delete(url)
        self.assertEqual(str(response.data), "{'success': 'message deleted'}")
        self.assertRaises(ObjectDoesNotExist, Message.objects.get, pk=1)

    @override_settings(DEBUG=False)
    def test_create_message(self):
        """
        Ensure we can create message with valid credentials
        """
        url = reverse('message-list')
        valid_credentials = {
            'chat_id': 2,
            'message': 'hi'
        }
        response_unauthorized = self.client.post(url, valid_credentials, follow=True)
        self.assertEqual(response_unauthorized.status_code, 403)

        token_test_user5 = Token.objects.get(user__username='test_user5')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_test_user5.key)
        response_authorized_another_user = self.client.post(url, valid_credentials, follow=True)
        self.assertEqual(response_authorized_another_user.status_code, 403)

        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(url, valid_credentials, follow=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.filter(chat__pk=2).count(), 2)

    @override_settings(DEBUG=False)
    def test_create_empty_message_fails(self):
        """
        Ensure we can't create empty message
        """
        invalid_credentials = {
            'chat_id': 2,
            'message': ''
        }
        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(reverse('message-list'), invalid_credentials, follow=True)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Message.objects.filter(chat__pk=2).count(), 1)

    @override_settings(DEBUG=False)
    def test_create_message_in_wrong_chat_fails(self):
        """
        Ensure we can't create message in wrong chat
        """
        invalid_credentials = {
            'chat_id': 3,
            'message': 'hi'
        }
        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(reverse('message-list'), invalid_credentials, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Message.objects.filter(chat__pk=3).count(), 0)

