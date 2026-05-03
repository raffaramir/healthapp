"""Signal handlers — notify admin on new registration, etc."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == Role.ADMIN or instance.is_superuser:
        return

    # Notify all admins of pending approval
    from apps.notifications.models import Notification
    admins = User.objects.filter(role=Role.ADMIN)
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title='New account awaiting approval',
            body=f'{instance.display_name} registered as {instance.get_role_display()}.',
            category='approval',
            link=f'/dashboard/admin/users/?status=pending',
        )
