from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import mixins, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .serializers import UserListSerializer, UserSerializer, ChatSerializer, MessageSerializer
from users.forms import UserRegisterForm
from messenger.models import Chat, Message


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    User API
    list: Get list of all users
    retrieve: Get certain user by username
    destroy: Delete certain user by username
    create: Add a new user
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    lookup_field = 'username'

    def list(self, request, *args, **kwargs):
        queryset = User.objects.all()
        serializer = UserListSerializer(queryset, many=True)

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    def retrieve(self, request, *args, username=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=username)
        serializer = UserListSerializer(user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            dict_for_form = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password1': serializer.validated_data['password'],
                'password2': serializer.validated_data['password']
            }
            form = UserRegisterForm(dict_for_form)
            if form.is_valid():
                form.save()
                return Response({'message': 'user created successfully'})
            else:
                return Response({"error": form.errors})
        else:
            return Response({"error": serializer.errors})


class UserDialoguesAPIView(ListAPIView):
    """
    Get list of all user's dialogues
    """
    serializer_class = ChatSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        return Chat.objects.filter(member__username=username)


class DialogueViewSet(mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    Dialogue API
    retrieve: Get certain dialogue by id
    destroy: Delete certain dialogue by id
    """
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        queryset = Message.objects.filter(chat__pk=pk)
        serializer = MessageSerializer(queryset, many=True)

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class MessageViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    Message API
    retrieve: Get certain message by id
    destroy: Delete certain message by id
    create: Add a new message
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

