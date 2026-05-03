from django.conf import settings
from django.db import models


class LabProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_profile'
    )
    lab_name = models.CharField(max_length=160)
    license_number = models.CharField(max_length=80, unique=True)
    professional_card = models.ImageField(upload_to='credentials/labs/', blank=True, null=True)
    services_offered = models.TextField(
        blank=True,
        help_text='Comma-separated list of test types offered',
    )
    home_visit_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lab_name']

    def __str__(self):
        return self.lab_name
