from django.contrib.auth.models import User
from ..models import Chat, Message


def interlocutor_exists(username: str):
    """
    The function defines if username is in database
    :param username: username
    :return: boolean
    """
    return User.objects.filter(username=username).exists()


def get_dialogue_chat(username: str, interlocutor: str):
    """
    The function
    :param username:
    :param interlocutor:
    :return:
    """
    user = User.objects.get(username=username)
    interlocutor_user = User.objects.get(username=interlocutor)

    dialog_chats_of_user = Chat.objects.filter(member=user).filter(type='D')
    dialog_chats_of_interlocutor = Chat.objects.filter(member=interlocutor_user).filter(type='D')
    common_chat = dialog_chats_of_user.intersection(dialog_chats_of_interlocutor)
    if common_chat:
        return common_chat[0]
    else:
        new_chat = Chat.objects.create()
        user.chat_set.add(new_chat)
        interlocutor_user.chat_set.add(new_chat)
        return new_chat


def delete_dialogue_chat(username: str, interlocutor: str):
    get_dialogue_chat(username, interlocutor).delete()


def save_message_to_db_get_message_dict(json_message):
    message = json_message['message']
    user = json_message['user']
    chat = json_message['chat_id']

    user_obj = User.objects.get(username=user)
    chat_obj = Chat.objects.get(pk=chat)

    new_message = Message.objects.create(author=user_obj, message=message, chat=chat_obj)

    return {
        'type': 'chat_message',
        'message': str(new_message.message),
        'user': str(new_message.author),
        'timestamp': str(new_message.pub_date),
        'message_id': str(new_message.id)
    }


def get_10_elder_messages(username, interlocutor, timestamp):
    chat = get_dialogue_chat(username, interlocutor)
    messages = Message.objects.filter(chat=chat).order_by('-pub_date').filter(pub_date__lt=timestamp)[:10]
    package_of_messages = []
    for message in messages:
        message_obj = {
            'user': message.author.username,
            'message': message.message,
            'timestamp': str(message.pub_date)
        }
        package_of_messages.append(message_obj)

    return package_of_messages


def get_count_of_unread_messages(chat):
    return Message.objects.filter(chat=chat).filter(is_read=False).count()


def get_messages_and_mark_them_read(username, chat):
    messages = Message.objects.filter(chat=chat).order_by('-pub_date')
    count_of_unread = get_count_of_unread_messages(chat)
    for message in messages[:count_of_unread]:
        if message.author.username != username and not message.is_read:
            message.is_read = True
            message.save()
    if count_of_unread > 15:
        # return reversed(messages[:count_of_unread + 1])
        return reversed(messages[:15])
    else:
        return reversed(messages[:15])


def get_all_chats(username):
    list_of_chats = []
    chats = Chat.objects.filter(member__username=username)

    for chat in chats:
        chat_obj = {
            'interlocutor': chat.member.all().exclude(username=username)[0],
            'unread_messages_count': get_count_of_unread_messages(chat),
            }
        last_message = Message.objects.filter(chat=chat).order_by('pub_date').last()

        if last_message:
            chat_obj['last_message'] = last_message
            chat_obj['last_message_timestamp'] = last_message.pub_date
            chat_obj['last_message_author'] = last_message.author
            list_of_chats.append(chat_obj)

    return sorted(list_of_chats, key=lambda x: x['last_message_timestamp'], reverse=True)
