from django.conf import settings
from django.db import models


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile'
    )
    specialty = models.CharField(max_length=120)
    license_number = models.CharField(max_length=80, unique=True)
    professional_card = models.ImageField(upload_to='credentials/doctors/', blank=True, null=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    home_visit_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_available = models.BooleanField(default=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating_avg', '-years_of_experience']

    def __str__(self):
        return f'Dr. {self.user.display_name} - {self.specialty}'
