from django.contrib.auth.models import User

from ..models import Chat, Message


def interlocutor_exists(username: str) -> bool:
    """
    The function defines if username is in database
    :param username: username of user
    :return: boolean
    """
    return User.objects.filter(username=username).exists()


def get_dialogue_chat(username: str, interlocutor: str) -> Chat:
    """
    The function finds the dialogue which is common for username and interlocutor or creates new one
    :param username: username of user
    :param interlocutor: username of interlocutor
    :return: Chat instance
    """
    user = User.objects.get(username=username)
    interlocutor_user = User.objects.get(username=interlocutor)

    dialogue_chat = Chat.objects.filter(chat_type='D').filter(member=user).filter(member=interlocutor_user)

    if dialogue_chat:
        return dialogue_chat[0]
    else:
        new_dialogue_chat = Chat.objects.create()
        user.chat_set.add(new_dialogue_chat)
        interlocutor_user.chat_set.add(new_dialogue_chat)
        return new_dialogue_chat


def delete_dialogue_chat(username: str, interlocutor: str):
    """
    The function finds the dialogue which is common for username and interlocutor and removes it from db
    :param username: username of user
    :param interlocutor: username of interlocutor
    """
    get_dialogue_chat(username, interlocutor).delete()


def save_message_to_db_get_message_dict(json_message: dict) -> dict:
    """
    The function for consumer. Saves message from client to db and returns massage
    as data from db with timestamp as a dict. This data then sends like message to the group by web socket
    :param json_message: message from client, json serialized to dict
    :return: dict with fields of saved to db message
    """
    message = json_message['message']
    user = json_message['user']
    chat = json_message['chat_id']

    user_obj = User.objects.get(username=user)
    chat_obj = Chat.objects.get(pk=chat)

    new_message = Message.objects.create(author=user_obj, message=message, chat=chat_obj)

    return {
        'type': 'chat_message',
        'message': new_message.message,
        'user': new_message.author.username,
        'timestamp': str(new_message.pub_date),
        'message_id': new_message.id
        }



def get_10_elder_messages(username: str, interlocutor: str, timestamp: str, amount: int = 10) -> list:
    """
    The function takes from db specified amount (10 by default) elder messages since specified timestamp
    :param username: username of user
    :param interlocutor: username of interlocutor
    :param timestamp: timestamp of the last message
    :param amount: the maximal amount of returned messages (10 by default)
    :return: list of dicts of parsed messages
    """
    chat = get_dialogue_chat(username, interlocutor)
    messages = Message.objects.filter(chat=chat).order_by('-pub_date').filter(pub_date__lt=timestamp)[:amount]
    package_of_messages = []
    for message in messages:
        message_obj = {
            'user': message.author.username,
            'message': message.message,
            'timestamp': str(message.pub_date)
        }
        package_of_messages.append(message_obj)
    return package_of_messages


def check_if_dialogue_is_empty_then_delete(chat: Chat):
    """
    The function checks the amount of messages in specified chat and deletes it if there is none
    :param chat: Chat instance
    """
    if not Message.objects.filter(chat=chat).count():
        Chat.objects.get(pk=chat).delete()


def get_count_of_unread_messages(chat: Chat) -> int:
    """
    The function counts the amount of unread messages in a specified chat
    :return: amount of unread messages
    """
    return Message.objects.filter(chat=chat).filter(is_read=False).count()


def get_messages_and_mark_them_read(username: str, chat: Chat, amount: int = 15) -> list:
    """
    The function returns last messages of specified chat and mark them as read if their author
    does not match with user
    :param username: username of user
    :param chat: Chat instance
    :param amount: the maximal amount of returned messages (15 by default)
    :return: list of last messages (Message instances)
    """
    count_of_unread = get_count_of_unread_messages(chat)
    messages = Message.objects.filter(chat=chat).order_by('-pub_date')
    for message in messages[:count_of_unread]:
        if message.author.username != username and not message.is_read:
            message.is_read = True
            message.save()
    return sorted(messages[:amount], key=lambda x: x.pub_date)


def update_message_read(message_id: int):
    """
    The function marks the message with specified id as read
    :param message_id: Id if a specified message
    """
    Message.objects.filter(pk=message_id).update(is_read=True)


def get_all_chats(username: str) -> list:
    """
    The function gets chats if specified user and parses them for dict structures with current brief information
    :param username: username of user
    :return: list of dicts that contain username of interlocutor in certain chat, amount of unread messages,
    last message, last_message_timestamp and last_message_author
    """
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
