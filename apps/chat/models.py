from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """1:1 conversation between two users (typically patient and doctor/pharmacist)."""

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        names = ', '.join(p.display_name for p in self.participants.all()[:3])
        return f'Conversation #{self.pk} ({names})'

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['conversation', 'created_at'])]

    def __str__(self):
        return f'{self.sender.display_name}: {self.body[:50]}'

    @property
    def is_image(self):
        if not self.attachment:
            return False
        ext = self.attachment.name.lower().rsplit('.', 1)[-1]
        return ext in ('jpg', 'jpeg', 'png', 'gif', 'webp')
