from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from .services.chat_services import interlocutor_exists, get_messages_and_mark_them_read, get_all_chats, \
    get_dialogue_chat, delete_dialogue_chat, get_10_elder_messages
from django.contrib.auth.mixins import LoginRequiredMixin


class MainView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        chats = get_all_chats(request.user.username)
        return render(request, 'messenger/main.html', {'chats': chats})

    def post(self, request):
        interlocutor = request.POST.get('interlocutor_username')
        if interlocutor_exists(interlocutor):
            return JsonResponse({'interlocutor_username': interlocutor}, status=200)
        else:
            return JsonResponse({'interlocutor_username': None}, status=404)


class ChatView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, interlocutor=None):
        chat = get_dialogue_chat(request.user.username, interlocutor)
        messages = get_messages_and_mark_them_read(request.user.username, chat.id)
        return render(request, 'messenger/chat.html', {'chat_id': chat.id,
                                                       'messages': messages,
                                                       'interlocutor': interlocutor})

    def post(self, request, interlocutor=None):
        if request.POST.get('date'):
            datestamp = request.POST.get('date')
            messages = get_10_elder_messages(request.user.username, interlocutor, datestamp)
            if messages:
                return JsonResponse({'messages': messages}, status=200)
            else:
                return JsonResponse({'messages': None}, status=204)

        elif request.POST.get('interlocutor_username'):
            new_interlocutor = request.POST.get('interlocutor_username')
            if interlocutor_exists(new_interlocutor):
                return JsonResponse({'interlocutor_username': new_interlocutor}, status=200)
            else:
                return JsonResponse({'interlocutor_username': None}, status=404)


class DeleteChatView(LoginRequiredMixin, View):

    def get(self, request, interlocutor):
        delete_dialogue_chat(request.user.username, interlocutor)
        return redirect('main')
