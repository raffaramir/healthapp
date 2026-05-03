from django.contrib import admin
from .models import Conversation, ChatMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_message_at', 'created_at')
    filter_horizontal = ('participants',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'body_preview', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('body', 'sender__email')

    @admin.display(description='Body')
    def body_preview(self, obj):
        return (obj.body or '[file]')[:60]
