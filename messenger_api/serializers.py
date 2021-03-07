from rest_framework import serializers
from django.contrib.auth.models import User

from messenger.models import Chat, Message


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(style={"input_type": "password"}, required=True)
    password2 = serializers.CharField(style={"input_type": "password"}, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        extra_kwargs = {'password1': {'write_only': True},
                        'password2': {'write_only': True}}


class ChatSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField(many=True)

    class Meta:
        model = Chat
        fields = '__all__'


class ChatCreateSerializer(serializers.ModelSerializer):
    member = serializers.CharField(required=True)

    class Meta:
        model = Chat
        fields = ('member', 'chat_type')


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    chat = ChatSerializer()

    class Meta:
        model = Message
        fields = '__all__'


class MessageListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Message
        exclude = ('chat',)


class MessageCreateSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(required=True)
    message = serializers.CharField(required=True)

    class Meta:
        model = Message
        fields = ('chat_id', 'message')
