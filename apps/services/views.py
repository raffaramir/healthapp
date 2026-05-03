from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.accounts.permissions import role_required
from apps.accounts.models import Role
from apps.notifications.models import Notification

from .models import ServiceRequest, ServiceType, RequestStatus, Review
from .forms import SERVICE_FORM_MAP, ProviderResponseForm, ReviewForm


# ─── PATIENT VIEWS ───────────────────────────────────────────────

@role_required(Role.PATIENT)
def request_select(request):
    """Choose service type to request."""
    return render(request, 'services/request_select.html', {
        'services': [(k, v[0]) for k, v in SERVICE_FORM_MAP.items()],
    })


@role_required(Role.PATIENT)
def request_create(request, service_type):
    if service_type not in SERVICE_FORM_MAP:
        messages.error(request, 'Unknown service type.')
        return redirect('services:request_select')

    label, form_cls = SERVICE_FORM_MAP[service_type]
    initial = {'address': request.user.address}
    form = form_cls(request.POST or None, request.FILES or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        sr = form.save(commit=False)
        sr.patient = request.user
        sr.service_type = service_type
        if not sr.address:
            sr.address = request.user.address
        sr.save()

        # Notify available providers of matching role
        target_role = {
            ServiceType.DOCTOR_HOME: Role.DOCTOR,
            ServiceType.LAB_HOME: Role.LAB,
            ServiceType.PHARMACY_ORDER: Role.PHARMACIST,
            ServiceType.CONSULTATION: Role.DOCTOR,
        }.get(service_type)

        if target_role:
            from apps.accounts.models import User
            providers = User.objects.filter(role=target_role, is_approved=True, is_active=True)
            for p in providers:
                Notification.objects.create(
                    user=p, title=f'New {label} request',
                    body=f'Patient {request.user.display_name}: {sr.title}',
                    category='request', link=f'/services/provider/{sr.pk}/',
                )

        messages.success(request, f'Your {label.lower()} request has been submitted.')
        return redirect('services:request_detail', pk=sr.pk)

    return render(request, 'services/request_form.html', {
        'form': form, 'service_type': service_type, 'label': label,
    })


@login_required
def request_list(request):
    """List requests visible to current user (patient sees own, provider sees their queue, admin sees all)."""
    user = request.user
    qs = ServiceRequest.objects.select_related('patient', 'provider')

    if user.is_admin_role:
        pass
    elif user.is_patient:
        qs = qs.filter(patient=user)
    else:
        # Provider — see unassigned matching their role + their assigned ones
        type_map = {
            Role.DOCTOR: [ServiceType.DOCTOR_HOME, ServiceType.CONSULTATION],
            Role.LAB: [ServiceType.LAB_HOME],
            Role.PHARMACIST: [ServiceType.PHARMACY_ORDER],
        }
        allowed = type_map.get(user.role, [])
        qs = qs.filter(
            Q(provider=user) |
            Q(provider__isnull=True, service_type__in=allowed, status=RequestStatus.PENDING)
        )

    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    return render(request, 'services/request_list.html', {
        'requests': qs[:100],
        'status_filter': status,
        'statuses': RequestStatus.choices,
    })


@login_required
def request_detail(request, pk):
    user = request.user
    sr = get_object_or_404(ServiceRequest.objects.select_related('patient', 'provider'), pk=pk)

    # Visibility check
    if not (user.is_admin_role or sr.patient == user or sr.provider == user
            or (sr.provider is None and not user.is_patient)):
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('services:request_list')

    can_review = (sr.patient == user and sr.status == RequestStatus.COMPLETED
                  and not hasattr(sr, 'review'))
    review_form = ReviewForm(request.POST or None) if can_review else None

    if can_review and request.method == 'POST' and 'submit_review' in request.POST and review_form.is_valid():
        review = review_form.save(commit=False)
        review.service_request = sr
        review.save()
        messages.success(request, 'Thanks for your review!')
        return redirect('services:request_detail', pk=pk)

    return render(request, 'services/request_detail.html', {
        'sr': sr, 'review_form': review_form, 'can_review': can_review,
    })


@role_required(Role.PATIENT)
def request_cancel(request, pk):
    sr = get_object_or_404(ServiceRequest, pk=pk, patient=request.user)
    if sr.status in (RequestStatus.PENDING, RequestStatus.ACCEPTED):
        sr.status = RequestStatus.CANCELLED
        sr.save(update_fields=['status'])
        if sr.provider:
            Notification.objects.create(
                user=sr.provider, title='Request cancelled',
                body=f'{sr.patient.display_name} cancelled request #{sr.pk}.',
                category='request',
            )
        messages.info(request, 'Request cancelled.')
    else:
        messages.warning(request, 'This request can no longer be cancelled.')
    return redirect('services:request_detail', pk=pk)


# ─── PROVIDER VIEWS ───────────────────────────────────────────────

@login_required
def provider_action(request, pk):
    """Accept / reject / complete a service request."""
    user = request.user
    if user.is_patient:
        messages.error(request, 'Only providers can perform this action.')
        return redirect('services:request_list')

    sr = get_object_or_404(ServiceRequest, pk=pk)
    action = request.POST.get('action')

    if action == 'accept' and sr.status == RequestStatus.PENDING and sr.provider is None:
        sr.provider = user
        sr.status = RequestStatus.ACCEPTED
        sr.accepted_at = timezone.now()
        sr.save()
        Notification.objects.create(
            user=sr.patient, title='Request accepted',
            body=f'{user.display_name} accepted your request "{sr.title}".',
            category='request', link=f'/services/{sr.pk}/',
        )
        messages.success(request, 'Request accepted.')

    elif action == 'reject' and sr.status == RequestStatus.PENDING:
        sr.status = RequestStatus.REJECTED
        sr.rejection_reason = request.POST.get('reason', '')
        sr.save()
        Notification.objects.create(
            user=sr.patient, title='Request rejected',
            body=f'Your request "{sr.title}" was rejected.', category='request',
        )
        messages.info(request, 'Request rejected.')

    elif action == 'start' and sr.provider == user and sr.status == RequestStatus.ACCEPTED:
        sr.status = RequestStatus.IN_PROGRESS
        sr.save(update_fields=['status'])
        messages.success(request, 'Request marked as in progress.')

    elif action == 'complete' and sr.provider == user and sr.status in (RequestStatus.ACCEPTED, RequestStatus.IN_PROGRESS):
        sr.status = RequestStatus.COMPLETED
        sr.completed_at = timezone.now()
        sr.final_cost = request.POST.get('final_cost') or sr.estimated_cost
        sr.save()
        Notification.objects.create(
            user=sr.patient, title='Service completed',
            body=f'Your request "{sr.title}" was marked completed.',
            category='request', link=f'/services/{sr.pk}/',
        )
        messages.success(request, 'Request completed.')

    return redirect('services:request_detail', pk=sr.pk)


@login_required
def provider_respond(request, pk):
    """Provider provides estimated cost / notes."""
    sr = get_object_or_404(ServiceRequest, pk=pk, provider=request.user)
    form = ProviderResponseForm(request.POST or None, instance=sr)
    if request.method == 'POST' and form.is_valid():
        form.save()
        Notification.objects.create(
            user=sr.patient, title='Provider update',
            body=f'{request.user.display_name} updated your request.',
            category='request', link=f'/services/{sr.pk}/',
        )
        messages.success(request, 'Response sent.')
        return redirect('services:request_detail', pk=pk)
    return render(request, 'services/provider_respond.html', {'form': form, 'sr': sr})
