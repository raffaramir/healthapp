"""WebSocket consumer for real-time chat."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import Conversation, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        is_member = await self._is_member()
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            return

        body = (data.get('body') or '').strip()
        if not body:
            return

        msg = await self._save_message(body)

        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message_id': msg.id,
            'body': body,
            'sender_id': self.user.id,
            'sender_name': self.user.display_name,
            'created_at': msg.created_at.isoformat(),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'body': event['body'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at'],
            'is_self': event['sender_id'] == self.user.id,
        }))

    @database_sync_to_async
    def _is_member(self):
        return Conversation.objects.filter(
            pk=self.conversation_id, participants=self.user
        ).exists()

    @database_sync_to_async
    def _save_message(self, body):
        convo = Conversation.objects.get(pk=self.conversation_id)
        msg = ChatMessage.objects.create(conversation=convo, sender=self.user, body=body)
        convo.last_message_at = timezone.now()
        convo.save(update_fields=['last_message_at'])
        return msg
