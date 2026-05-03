from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.accounts.permissions import role_required
from apps.accounts.models import Role
from .models import PatientProfile, MedicationReminder, MedicalRecord
from .forms import MedicationReminderForm, MedicalRecordForm, PatientProfileForm


@role_required(Role.PATIENT)
def medication_list(request):
    profile = request.user.patient_profile
    meds = profile.medications.all()
    return render(request, 'patients/medication_list.html', {'medications': meds})


@role_required(Role.PATIENT)
def medication_create(request):
    profile = request.user.patient_profile
    form = MedicationReminderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        med = form.save(commit=False)
        med.patient = profile
        # set next dose to start_date 8 AM (or now if same day)
        start = form.cleaned_data['start_date']
        first = timezone.make_aware(datetime.combine(start, datetime.min.time()).replace(hour=8))
        med.next_dose_at = first if first > timezone.now() else timezone.now() + timedelta(hours=med.hours_per_dose())
        med.save()
        messages.success(request, 'Medication reminder added.')
        return redirect('patients:medication_list')
    return render(request, 'patients/medication_form.html', {'form': form, 'mode': 'create'})


@role_required(Role.PATIENT)
def medication_delete(request, pk):
    med = get_object_or_404(MedicationReminder, pk=pk, patient=request.user.patient_profile)
    if request.method == 'POST':
        med.delete()
        messages.success(request, 'Medication reminder removed.')
    return redirect('patients:medication_list')


@role_required(Role.PATIENT)
def medication_toggle(request, pk):
    med = get_object_or_404(MedicationReminder, pk=pk, patient=request.user.patient_profile)
    med.is_active = not med.is_active
    med.save(update_fields=['is_active'])
    return redirect('patients:medication_list')


@role_required(Role.PATIENT)
def records_list(request):
    profile = request.user.patient_profile
    records = profile.medical_records.all()
    form = MedicalRecordForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        rec = form.save(commit=False)
        rec.patient = profile
        rec.save()
        messages.success(request, 'Medical record uploaded.')
        return redirect('patients:records')
    return render(request, 'patients/records.html', {'records': records, 'form': form})


@role_required(Role.PATIENT)
def health_profile(request):
    profile = request.user.patient_profile
    form = PatientProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Health profile updated.')
        return redirect('patients:health_profile')
    return render(request, 'patients/health_profile.html', {'form': form, 'profile': profile})
