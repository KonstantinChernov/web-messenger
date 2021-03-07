from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import MainView, ChatView, DeleteChatView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('chats/<str:interlocutor>/', ChatView.as_view(), name='chat'),
    path("chats/delete/<str:interlocutor>/", DeleteChatView.as_view(), name="delete"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
