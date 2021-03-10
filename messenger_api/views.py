from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework import mixins, viewsets, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .serializers import (UserListSerializer,
                          UserRegisterSerializer,
                          MessageSerializer,
                          MessageListSerializer,
                          MessageCreateSerializer,
                          ChatSerializer,
                          ChatCreateSerializer)
from users.forms import UserRegisterForm
from messenger.models import Chat, Message


for user in User.objects.all():
    Token.objects.get_or_create(user=user)


class UserRegisterAPIView(CreateAPIView):
    """
    Register API
    """
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new user
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            form = UserRegisterForm(serializer.validated_data)
            if form.is_valid():
                form.save()
                return Response({'success': 'user created successfully'})
            else:
                return Response(form.errors)
        else:
            return Response(serializer.errors)


class UserAuthTokenLogin(CreateAPIView):
    """
    Token Authorisation API (Login)
    """
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Get Token by username and password
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        valid_user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=valid_user)
        return Response({
            'token': token.key,
        })


class UsersViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    User API
    list: Get list of all interlocutors of user
    retrieve: Get certain user by username
    """
    serializer_class = UserListSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    lookup_field = 'username'

    def list(self, request, *args, **kwargs):
        username = request.user
        queryset = [chat.member.all().exclude(username=username)[0] for chat
                    in Chat.objects.filter(member__username=username)]
        serializer = self.serializer_class(queryset, many=True)

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class ChatsViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    Dialogue API
    create: Add a new chat
    list: Get list of all chats of user
    retrieve: Get certain chat by id
    destroy: Delete certain chat by id
    """
    serializer_class = ChatCreateSerializer
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            interlocutor_username = serializer.validated_data['member']
            try:
                interlocutor = User.objects.get(username=interlocutor_username)
                dialogue_chat = Chat.objects\
                    .filter(chat_type='D')\
                    .filter(member=request.user)\
                    .filter(member=interlocutor)
                if dialogue_chat:
                    return Response({"error": "chat with this user already exists"}, status=status.HTTP_409_CONFLICT)
                else:
                    new_dialogue_chat = Chat.objects.create()
                    request.user.chat_set.add(new_dialogue_chat)
                    interlocutor.chat_set.add(new_dialogue_chat)
                    return Response({'success': 'chat created successfully'})
            except ObjectDoesNotExist:
                return Response({"error": "user is not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors)

    def list(self, request, *args, **kwargs):
        username = request.user
        queryset = self.queryset.filter(member__username=username)
        serializer = ChatSerializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            if Chat.objects.get(pk=pk) in request.user.chat_set.all():
                queryset = Message.objects.filter(chat__pk=pk)
                serializer = MessageListSerializer(queryset, many=True)

                page = self.paginate_queryset(serializer.data)
                return self.get_paginated_response(page)
            else:
                return Response({"error": "HTTP 403 Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({"error": "chat is not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            chat = Chat.objects.get(pk=pk)
            if chat in request.user.chat_set.all():
                chat.delete()
                return Response({"success": "chat deleted"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "HTTP 403 Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({"error": "message is not found"}, status=status.HTTP_404_NOT_FOUND)


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
    serializer_class = MessageCreateSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            message = Message.objects.get(pk=pk)
            if message.chat in request.user.chat_set.all():
                serializer = MessageSerializer(message)
                return Response(serializer.data)
            else:
                return Response({"error": "HTTP 403 Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({"error": "message is not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        if request.data['message']:
            serializer = MessageCreateSerializer(data=request.data)
            if serializer.is_valid():
                chat_id = serializer.validated_data['chat_id']
                message = serializer.validated_data['message']
                try:
                    chat = Chat.objects.get(pk=chat_id)
                    if chat in request.user.chat_set.all():
                        Message.objects.create(author=request.user, chat=chat, message=message)
                        return Response({"success": "message created"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": "HTTP 403 Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
                except ObjectDoesNotExist:
                    return Response({"error": "chat is not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs['pk']

        try:
            message = Message.objects.get(pk=pk)
            if message.author == request.user:
                message.delete()
                return Response({"success": "message deleted"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "HTTP 403 Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({"error": "message is not found"}, status=status.HTTP_404_NOT_FOUND)
