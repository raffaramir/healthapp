from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Category(models.TextChoices):
        ACCOUNT = 'account', 'Account'
        REQUEST = 'request', 'Service request'
        CHAT = 'chat', 'Chat message'
        APPROVAL = 'approval', 'Approval'
        MEDICATION = 'medication', 'Medication'
        SYSTEM = 'system', 'System'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM)
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f'{self.user.email}: {self.title}'

    @property
    def icon(self):
        icons = {
            'account': '👤', 'request': '📋', 'chat': '💬',
            'approval': '✅', 'medication': '💊', 'system': '🔔',
        }
        return icons.get(self.category, '🔔')
