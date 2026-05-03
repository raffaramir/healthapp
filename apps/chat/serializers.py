from rest_framework import serializers
from .models import Conversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.display_name', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation', 'sender', 'sender_name', 'body',
                  'attachment', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message_at', 'last_message', 'created_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return ChatMessageSerializer(msg).data if msg else None
