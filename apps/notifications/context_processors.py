def notifications_processor(request):
    if not request.user.is_authenticated:
        return {}
    unread = request.user.notifications.filter(is_read=False).count()
    return {
        'nav_unread_notifications': unread,
        'nav_recent_notifications': request.user.notifications.all()[:5],
    }
