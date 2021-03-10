from django.test import TestCase
from django.urls import reverse
from django.test.utils import override_settings

from messenger.models import User, Chat, Message


class ViewsTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'test_user',
            'password': 'secret_password'
        }
        self.test_user1 = User.objects.create_user(**self.credentials)
        self.test_user2 = User.objects.create_user(username='test_user2', password='secret_password')
        self.test_user3 = User.objects.create_user(username='test_user3', password='secret_password')
        self.chat_1 = Chat.objects.create()
        self.test_user1.chat_set.add(self.chat_1)
        self.test_user2.chat_set.add(self.chat_1)
        for i in range(25):
            Message.objects.create(author=self.test_user1, message=f'hello{i}', chat=self.chat_1)

        self.chat_2 = Chat.objects.create()
        self.test_user1.chat_set.add(self.chat_2)
        self.test_user3.chat_set.add(self.chat_2)
        Message.objects.create(author=self.test_user1, message='hello', chat=self.chat_2)

    @override_settings(DEBUG=False)
    def test_main_page_unauthorised(self):
        """
        Testing main page for redirecting unauthorized user to the login page
        """
        response_unauthorised_redirected = self.client.get(reverse('main'), follow=True)
        self.assertEqual(response_unauthorised_redirected.status_code, 200)
        self.assertTemplateUsed(response_unauthorised_redirected, 'users/login.html')

    @override_settings(DEBUG=False)
    def test_main_page_authorised(self):
        """
        Testing main page for authorized user to show right template with his chats
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)

        response_authorised = self.client.get(reverse('main'))
        self.assertEqual(response_authorised.status_code, 200)
        self.assertTemplateUsed(response_authorised, 'messenger/main.html')

        # check the amount of received messages
        self.assertEqual(len(response_authorised.context['chats']), 2)

    @override_settings(DEBUG=False)
    def test_interlocutor_searching(self):
        """
        Testing correct responses for searching existing and non-existing users
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)

        def interlocutor_searching(url):
            # check the status code if the user with specified username exists
            response_searching_right = self.client.post(url, {'interlocutor_username': 'test_user2'},
                                                        follow=True)
            self.assertEqual(response_searching_right.status_code, 200)

            # check the status code otherwise
            response_searching_wrong = self.client.post(url, {'interlocutor_username': 'wrong_name'},
                                                        follow=True)
            self.assertEqual(response_searching_wrong.status_code, 404)

        interlocutor_searching(reverse('main'))
        interlocutor_searching(reverse('chat', args=['test_user2']))

    @override_settings(DEBUG=False)
    def test_delete_chat(self):
        """
        Testing correct deleting of the chat
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)

        response_delete = self.client.get(reverse('delete', args=['test_user2']),
                                          follow=True)
        self.assertEqual(response_delete.status_code, 200)
        self.assertTemplateUsed(response_delete, 'messenger/main.html')

        # check the absence of deleted interlocutor in the list of chats
        self.assertNotIn(self.chat_1, self.test_user1.chat_set.all())
        for chat in response_delete.context['chats']:
            self.assertNotEqual(chat['interlocutor'], self.test_user2)

    @override_settings(DEBUG=False)
    def test_logout(self):
        """
        Testing correct logout of user
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)

        # logout
        response_logout = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response_logout.status_code, 200)
        self.assertTemplateUsed(response_logout, 'users/login.html')
        self.assertFalse(response_logout.context['user'].is_active)

    @override_settings(DEBUG=False)
    def test_chat_view(self):
        """
        Testing correct display of pre-loaded last messages in the chat
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)
        response_get_chat = self.client.get(reverse('chat', args=['test_user2']), follow=True)
        self.assertEqual(response_get_chat.status_code, 200)
        self.assertTemplateUsed(response_get_chat, 'messenger/chat.html')

        # check the amount of received messages
        self.assertEqual(len(response_get_chat.context['messages']), 15)

        # check the last message received is the last message of all conversation
        self.assertEqual(response_get_chat.context['messages'][14].message, 'hello24')

    @override_settings(DEBUG=False)
    def test_chat_view_history_loading(self):
        """
        Testing correct display of elder messages in the chat
        """
        # login
        self.client.post(reverse('login'), self.credentials, follow=True)
        response_get_chat = self.client.get(reverse('chat', args=['test_user2']), follow=True)

        timestamp_of_earliest = response_get_chat.context['messages'][0].pub_date
        response_get_elder_messages = self.client.post(reverse('chat', args=['test_user2']),
                                                       {'date': timestamp_of_earliest},
                                                       follow=True)
        # check the amount of received messages
        amount_of_elder_messages = len(response_get_elder_messages.json()["messages"])
        self.assertEqual(amount_of_elder_messages, 10)

        # check the last received message is the first of all conversation
        self.assertEqual(response_get_elder_messages.json()["messages"][amount_of_elder_messages - 1]["message"],
                         'hello0')

        # try to get history when its all is loaded
        timestamp_of_earliest_from_elders = response_get_elder_messages.json()["messages"][
            amount_of_elder_messages - 1]['timestamp']
        response_get_elder_messages_again = self.client.post(reverse('chat', args=['test_user2']),
                                                             {'date': timestamp_of_earliest_from_elders},
                                                             follow=True)
        self.assertEqual(response_get_elder_messages_again.status_code, 204)
