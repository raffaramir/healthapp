from django.conf import settings
from django.db import models


class BloodGroup(models.TextChoices):
    A_POS = 'A+', 'A+'
    A_NEG = 'A-', 'A-'
    B_POS = 'B+', 'B+'
    B_NEG = 'B-', 'B-'
    AB_POS = 'AB+', 'AB+'
    AB_NEG = 'AB-', 'AB-'
    O_POS = 'O+', 'O+'
    O_NEG = 'O-', 'O-'
    UNKNOWN = 'UNK', 'Unknown'


class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile'
    )
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=120)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=160, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Patient: {self.user.display_name}'

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class MedicationReminder(models.Model):
    class Frequency(models.TextChoices):
        ONCE = 'once', 'Once daily'
        TWICE = 'twice', 'Twice daily'
        THRICE = 'thrice', 'Three times daily'
        FOUR = 'four', 'Four times daily'
        CUSTOM = 'custom', 'Custom (every N hours)'

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='medications'
    )
    medication_name = models.CharField(max_length=160)
    dosage = models.CharField(max_length=80, help_text='e.g. 500mg, 1 tablet')
    frequency = models.CharField(max_length=10, choices=Frequency.choices, default=Frequency.ONCE)
    interval_hours = models.PositiveSmallIntegerField(default=24, help_text='used when frequency is custom')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_dose_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', 'next_dose_at']

    def __str__(self):
        return f'{self.medication_name} ({self.dosage})'

    def hours_per_dose(self):
        mapping = {'once': 24, 'twice': 12, 'thrice': 8, 'four': 6}
        return mapping.get(self.frequency, self.interval_hours or 24)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name='medical_records'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='medical_records/', null=True, blank=True)
    record_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-record_date']

    def __str__(self):
        return self.title
