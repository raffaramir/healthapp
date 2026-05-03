from django import forms
from apps.accounts.forms import StyledFormMixin
from .models import MedicationReminder, MedicalRecord, PatientProfile


class MedicationReminderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MedicationReminder
        fields = ['medication_name', 'dosage', 'frequency', 'interval_hours',
                  'start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class MedicalRecordForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['title', 'description', 'file', 'record_date']
        widgets = {
            'record_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PatientProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['blood_group', 'allergies', 'chronic_conditions',
                  'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
        }
