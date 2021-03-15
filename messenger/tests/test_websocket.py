# from asgiref.sync import sync_to_async
# from django.contrib.auth.models import User
# from django.test import TestCase
# from channels.testing import WebsocketCommunicator
# from my_web_messenger.routing import application
#
#
# class MyTests(TestCase):
#     def setUp(self):
#         self.credentials = {
#             'username': 'test_user',
#             'password': 'secret_password'
#         }
#         self.test_user1 = User.objects.create_user(**self.credentials)
#         self.test_user2 = User.objects.create_user(username='test_user2', password='secret_password')
#
#         self.chat_1 = Chat.objects.create(pk=1)
#         self.test_user1.chat_set.add(self.chat_1)
#         self.test_user2.chat_set.add(self.chat_1)
#
#     async def test_websocket(self):
#         communicator = WebsocketCommunicator(application, "/ws/chat/1/")
#
#         connected, subprotocol = await communicator.connect()
#
#         assert connected
#
#         # results = await sync_to_async(User.objects.get)(username='test_user')
#         # print(results.username)
#
#         # await communicator.send_json_to({"message": "hello",
#         #                                  "user": results.username,
#         #                                  "chat_id": 1})
#
#         # response = await communicator.receive_json_from()
#         # assert response['message'] == "hello"
#
#         await communicator.disconnect()
#         assert not connected
