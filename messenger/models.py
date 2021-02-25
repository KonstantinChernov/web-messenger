from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Chat(models.Model):
    DIALOG = 'D'
    CHAT = 'C'
    CHAT_TYPE_CHOICES = (
        (DIALOG, 'dialog'),
        (CHAT, 'chat')
    )

    type = models.CharField(
        'type',
        max_length=1,
        choices=CHAT_TYPE_CHOICES,
        default=DIALOG,

    )
    member = models.ManyToManyField(User, verbose_name='member')


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_author', null=True)
    message = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages', null=True)
    pub_date = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message
