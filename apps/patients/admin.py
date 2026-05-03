from django.contrib import admin
from .models import PatientProfile, MedicationReminder, MedicalRecord


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'blood_group', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('blood_group',)


@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ('medication_name', 'patient', 'frequency', 'next_dose_at', 'is_active')
    list_filter = ('is_active', 'frequency')
    search_fields = ('medication_name', 'patient__user__email')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'record_date')
    search_fields = ('title', 'patient__user__email')
