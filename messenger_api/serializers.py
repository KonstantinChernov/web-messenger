from rest_framework import serializers
from django.contrib.auth.models import User

from messenger.models import Chat, Message


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class ChatSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField(many=True)

    class Meta:
        model = Chat
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessageListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = '__all__'


class ChatMessagesListSerializer(serializers.ModelSerializer):
    chat_messages = MessageListSerializer(many=True)
    member = serializers.StringRelatedField(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'member', 'chat_messages')
