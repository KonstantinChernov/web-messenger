from django.urls import path
from rest_framework import routers
from .yasg import schema_view

from .views import UserViewSet, UserDialoguesAPIView, DialogueViewSet, MessageViewSet


router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'dialogues', DialogueViewSet, basename='dialogue')
router.register(r'message', MessageViewSet, basename='message')

urlpatterns = [
    path('', schema_view.with_ui('swagger')),
    path('users/<str:username>/dialogues', UserDialoguesAPIView.as_view()),
]

urlpatterns += router.urls

