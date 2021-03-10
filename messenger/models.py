from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now


User = get_user_model()


class Chat(models.Model):

    class ChatType(models.TextChoices):
        DIALOG = 'D', 'dialogue'
        CHAT = 'C', 'common'

    chat_type = models.CharField(
        'type',
        max_length=1,
        choices=ChatType.choices,
        default=ChatType.DIALOG,
    )
    member = models.ManyToManyField(User, verbose_name='member')

    def __str__(self):
        return f'{self.pk}'


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_author', null=True)
    message = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages', null=True)
    pub_date = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        # return self.message
        return f'Message {self.pk} (chat: {self.chat}; author: {self.author}; published: {self.pub_date})'
