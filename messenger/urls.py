from django.urls import path
from .views import MainView, ChatView, DeleteChatView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('chats/', MainView.as_view(), name='main'),
    path('chats/<str:interlocutor>/', ChatView.as_view(), name='chat'),
    path("chats/delete/<str:interlocutor>/", DeleteChatView.as_view(), name="delete"),
    path("logout/", LogoutView.as_view(), name="logout"),
]


