from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from .services.chat_services import interlocutor_exists, get_messages_and_mark_them_read, get_all_chats, \
    get_dialogue_chat, delete_dialogue_chat
from django.contrib.auth.mixins import LoginRequiredMixin


class MainView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        chats = get_all_chats(request.user.username)
        return render(request, 'messenger/main.html', {'chats': chats})

    def post(self, request, interlocutor=None):
        interlocutor = request.POST.get('interlocutor_username')
        if interlocutor_exists(interlocutor):
            return JsonResponse({'interlocutor_username': interlocutor}, status=200)
        else:
            return JsonResponse({'interlocutor_username': None}, status=404)


class ChatView(MainView):

    def get(self, request, interlocutor=None):
        chat = get_dialogue_chat(request.user.username, interlocutor)
        messages = get_messages_and_mark_them_read(request.user.username, chat.id)
        return render(request, 'messenger/chat.html', {'chat_id': chat.id,
                                                       'messages': messages,
                                                       'interlocutor': interlocutor})


class DeleteChatView(LoginRequiredMixin, View):

    def get(self, request, interlocutor):
        delete_dialogue_chat(request.user.username, interlocutor)
        return redirect('main')
