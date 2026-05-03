"""Cron command — dispatches notifications for medications due now.

Run via:
    python manage.py dispatch_medication_reminders

Schedule every minute via your OS scheduler / celery-beat.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.patients.models import MedicationReminder
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = 'Dispatch medication reminders that are due'

    def handle(self, *args, **opts):
        now = timezone.now()
        due = MedicationReminder.objects.filter(
            is_active=True,
            next_dose_at__lte=now,
        ).select_related('patient__user')

        sent = 0
        for med in due:
            Notification.objects.create(
                user=med.patient.user,
                title=f'Medication reminder: {med.medication_name}',
                body=f"It's time to take {med.dosage} of {med.medication_name}.",
                category='medication',
                link='/patients/medications/',
            )
            med.next_dose_at = now + timedelta(hours=med.hours_per_dose())
            if med.end_date and med.next_dose_at.date() > med.end_date:
                med.is_active = False
            med.save(update_fields=['next_dose_at', 'is_active'])
            sent += 1

        self.stdout.write(self.style.SUCCESS(f'Dispatched {sent} medication reminder(s).'))
