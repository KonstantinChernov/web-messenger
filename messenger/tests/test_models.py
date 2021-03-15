from django.test import TestCase

from messenger.models import User, Chat, Message


class ModelTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'test_user',
            'password': 'secret_password'
        }
        self.test_user1 = User.objects.create_user(**self.credentials)
        self.test_user2 = User.objects.create_user(username='test_user2', password='secret_password')
        self.test_user3 = User.objects.create_user(username='test_user3', password='secret_password')

        self.chat_1 = Chat.objects.create(pk=1)
        self.test_user1.chat_set.add(self.chat_1)
        self.test_user2.chat_set.add(self.chat_1)
        for i in range(3):
            Message.objects.create(pk=i+1, author=self.test_user1, message=f'hello{i}', chat=self.chat_1)

        self.chat_2 = Chat.objects.create(pk=2)
        self.test_user1.chat_set.add(self.chat_2)
        self.test_user3.chat_set.add(self.chat_2)
        self.message = Message.objects.create(pk=4, author=self.test_user1, message='hello', chat=self.chat_2)

    def test_chat_type(self):
        self.assertEqual(self.chat_1.chat_type, 'D')
        self.assertEqual(self.chat_2.chat_type, 'D')

    def test_chat_str(self):
        self.assertEqual(str(self.chat_1), '1')
        self.assertEqual(str(self.chat_2), '2')

    def test_message_str(self):
        timestamp = self.message.pub_date
        self.assertEqual(str(self.message), f'Message 4 (chat: 2; author: test_user; published:'
                                            f' {timestamp})')

    def test_messages_ordering(self):
        list_messages = [message.message for message in Message.objects.filter(chat=self.chat_1)]
        self.assertListEqual(list_messages, ['hello0', 'hello1', 'hello2'])
