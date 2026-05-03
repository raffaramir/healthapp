from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()[:100]
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
@require_POST
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save(update_fields=['is_read'])
    if n.link:
        return redirect(n.link)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def api_unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread': count})


@login_required
def api_recent(request):
    items = list(request.user.notifications.all()[:10].values(
        'id', 'title', 'body', 'category', 'link', 'is_read', 'created_at'
    ))
    return JsonResponse({'notifications': items}, safe=False)
