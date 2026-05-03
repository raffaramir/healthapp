from rest_framework import viewsets, permissions
from .models import Conversation, ChatMessage
from .serializers import ConversationSerializer, ChatMessageSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.all()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ChatMessage.objects.filter(conversation__participants=self.request.user)
        convo = self.request.query_params.get('conversation')
        if convo:
            qs = qs.filter(conversation_id=convo)
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
