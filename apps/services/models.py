"""Service requests + appointments. One generic ServiceRequest with type field."""
from django.conf import settings
from django.db import models


class ServiceType(models.TextChoices):
    DOCTOR_HOME = 'doctor_home', 'Doctor at home'
    LAB_HOME = 'lab_home', 'Lab technician at home'
    PHARMACY_ORDER = 'pharmacy_order', 'Pharmacy order'
    CONSULTATION = 'consultation', 'Online consultation'


class RequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    IN_PROGRESS = 'in_progress', 'In progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    REJECTED = 'rejected', 'Rejected'


class Urgency(models.TextChoices):
    LOW = 'low', 'Low'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'High'
    EMERGENCY = 'emergency', 'Emergency'


class ServiceRequest(models.Model):
    """Generic service request — type discriminates pharmacy/doctor/lab."""

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='requests_made', limit_choices_to={'role': 'patient'}
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='requests_received',
    )

    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.NORMAL)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField(help_text='Service delivery address')
    preferred_datetime = models.DateTimeField(null=True, blank=True)

    # Pharmacy-specific
    prescription_image = models.ImageField(upload_to='prescriptions/', null=True, blank=True)
    prescription_text = models.TextField(blank=True)

    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Provider feedback
    provider_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    # Timeline
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['service_type']),
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['provider', 'status']),
        ]

    def __str__(self):
        return f'#{self.pk} {self.get_service_type_display()} - {self.patient.email}'

    @property
    def is_open(self):
        return self.status in (RequestStatus.PENDING, RequestStatus.ACCEPTED, RequestStatus.IN_PROGRESS)

    @property
    def status_color(self):
        colors = {
            'pending': '#FFAA00', 'accepted': '#22C55E', 'in_progress': '#10B981',
            'completed': '#16A34A', 'cancelled': '#6B7280', 'rejected': '#EF4444',
        }
        return colors.get(self.status, '#6B7280')


class Appointment(models.Model):
    """Scheduled appointment tied to an accepted service request."""

    service_request = models.OneToOneField(
        ServiceRequest, on_delete=models.CASCADE, related_name='appointment'
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    notes = models.TextField(blank=True)
    is_video = models.BooleanField(default=False)
    video_room_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f'Appointment {self.scheduled_at:%Y-%m-%d %H:%M} - {self.service_request}'


class Review(models.Model):
    """Patient review of completed service."""

    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
