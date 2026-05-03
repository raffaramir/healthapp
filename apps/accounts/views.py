"""Authentication views: login, register, logout, profile, email verification."""
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .forms import (
    LoginForm, PatientRegisterForm, DoctorRegisterForm,
    LabRegisterForm, PharmacistRegisterForm, ProfileForm
)
from .models import User, ActivityLog, Role


REGISTER_FORMS = {
    'patient': ('Patient', PatientRegisterForm),
    'doctor': ('Doctor', DoctorRegisterForm),
    'lab': ('Lab Technician', LabRegisterForm),
    'pharmacist': ('Pharmacist', PharmacistRegisterForm),
}


def _client_meta(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
    ua = request.META.get('HTTP_USER_AGENT', '')[:300]
    return ip, ua


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        ip, ua = _client_meta(request)
        ActivityLog.objects.create(user=user, action='login', ip_address=ip, user_agent=ua)
        messages.success(request, f'Welcome back, {user.display_name}!')
        return redirect('dashboard:home')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        ActivityLog.objects.create(user=request.user, action='logout')
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('landing')


def register_select(request):
    """Choose role to register as."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'accounts/register_select.html', {'roles': REGISTER_FORMS})


def register_view(request, role):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if role not in REGISTER_FORMS:
        messages.error(request, 'Invalid registration role.')
        return redirect('accounts:register_select')

    label, form_cls = REGISTER_FORMS[role]
    form = form_cls(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ip, ua = _client_meta(request)
        ActivityLog.objects.create(
            user=user, action='register',
            description=f'Registered as {role}', ip_address=ip, user_agent=ua,
        )
        messages.success(
            request,
            'Registration successful! Your account is pending administrator approval. '
            'You will receive a notification once approved.'
        )
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {
        'form': form, 'role': role, 'role_label': label,
    })


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


def verify_email(request, token):
    user = get_object_or_404(User, email_verification_token=token)
    if not user.is_email_verified:
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        messages.success(request, 'Email verified successfully.')
    else:
        messages.info(request, 'Email was already verified.')
    return redirect('accounts:login')
