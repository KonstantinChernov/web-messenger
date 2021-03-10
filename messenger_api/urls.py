from django.urls import path
from rest_framework import routers


from .yasg import schema_view

from .views import UsersViewSet, ChatsViewSet, MessageViewSet, UserRegisterAPIView, UserAuthTokenLogin

router = routers.SimpleRouter()
router.register(r'users', UsersViewSet, basename='user')
router.register(r'chats', ChatsViewSet, basename='chat')
router.register(r'message', MessageViewSet, basename='message')

urlpatterns = [
    path('', schema_view.with_ui('swagger')),
    path('register/', UserRegisterAPIView.as_view(), name='api_register'),
    path('login/', UserAuthTokenLogin.as_view(), name='api_login'),
]

urlpatterns += router.urls

