from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.accounts.models import User, Role
from .models import Conversation, ChatMessage


@login_required
def conversation_list(request):
    convos = (request.user.conversations
              .annotate(unread=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)))
              .order_by('-last_message_at', '-created_at'))
    return render(request, 'chat/conversation_list.html', {'conversations': convos})


@login_required
def start_conversation(request, user_id):
    """Open or create 1:1 conversation with given user."""
    other = get_object_or_404(User, pk=user_id, is_approved=True)
    if other == request.user:
        messages.error(request, 'Cannot chat with yourself.')
        return redirect('chat:conversation_list')

    convo = (Conversation.objects
             .filter(participants=request.user).filter(participants=other)
             .annotate(p_count=Count('participants')).filter(p_count=2).first())
    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, other)
    return redirect('chat:conversation', pk=convo.pk)


@login_required
def conversation_view(request, pk):
    convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
    other = convo.other_participant(request.user)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')
        if body or attachment:
            msg = ChatMessage.objects.create(
                conversation=convo, sender=request.user,
                body=body, attachment=attachment,
            )
            convo.last_message_at = msg.created_at
            convo.save(update_fields=['last_message_at'])
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=other, title=f'New message from {request.user.display_name}',
                body=body[:120] or '[attachment]', category='chat',
                link=f'/chat/{convo.pk}/',
            )
        return redirect('chat:conversation', pk=pk)

    # mark messages from other party as read
    ChatMessage.objects.filter(conversation=convo, is_read=False).exclude(sender=request.user).update(is_read=True)

    msgs = convo.messages.select_related('sender')
    return render(request, 'chat/conversation.html', {
        'conversation': convo, 'other': other, 'messages_list': msgs,
    })


@login_required
def chat_directory(request):
    """List potential chat partners — doctors and pharmacists for patients;
    patients in your queue for providers."""
    user = request.user
    if user.is_patient:
        partners = User.objects.filter(role__in=[Role.DOCTOR, Role.PHARMACIST], is_approved=True)
    elif user.is_admin_role:
        partners = User.objects.filter(is_approved=True).exclude(pk=user.pk)
    else:
        # provider — show patients with whom they have requests
        from apps.services.models import ServiceRequest
        patient_ids = ServiceRequest.objects.filter(provider=user).values_list('patient', flat=True).distinct()
        partners = User.objects.filter(pk__in=patient_ids)
    return render(request, 'chat/directory.html', {'partners': partners})
