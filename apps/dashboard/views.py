"""Role-aware dashboard. /dashboard/ dispatches based on role."""
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages

from apps.accounts.models import User, Role, ActivityLog
from apps.accounts.permissions import admin_required
from apps.services.models import ServiceRequest, RequestStatus, ServiceType
from apps.notifications.models import Notification


def landing(request):
    """Public marketing landing page. Authenticated users skip to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'landing.html')


@login_required
def home(request):
    user = request.user
    if user.is_admin_role:
        return admin_dashboard(request)
    if not user.is_approved:
        return redirect('dashboard:pending_approval')
    if user.is_patient:
        return patient_dashboard(request)
    return provider_dashboard(request)


@login_required
def pending_approval(request):
    return render(request, 'dashboard/pending_approval.html')


def patient_dashboard(request):
    user = request.user
    profile = getattr(user, 'patient_profile', None)
    requests_qs = ServiceRequest.objects.filter(patient=user)
    open_reqs = requests_qs.filter(status__in=[RequestStatus.PENDING, RequestStatus.ACCEPTED, RequestStatus.IN_PROGRESS])
    completed = requests_qs.filter(status=RequestStatus.COMPLETED).count()
    meds = profile.medications.filter(is_active=True)[:5] if profile else []

    return render(request, 'dashboard/patient.html', {
        'open_requests': open_reqs[:6],
        'open_count': open_reqs.count(),
        'completed_count': completed,
        'total_count': requests_qs.count(),
        'medications': meds,
        'recent_requests': requests_qs[:5],
    })


def provider_dashboard(request):
    user = request.user
    type_map = {
        Role.DOCTOR: [ServiceType.DOCTOR_HOME, ServiceType.CONSULTATION],
        Role.LAB: [ServiceType.LAB_HOME],
        Role.PHARMACIST: [ServiceType.PHARMACY_ORDER],
    }
    allowed = type_map.get(user.role, [])
    queue = ServiceRequest.objects.filter(
        provider__isnull=True, status=RequestStatus.PENDING, service_type__in=allowed
    )[:8]
    mine = ServiceRequest.objects.filter(provider=user)
    active = mine.filter(status__in=[RequestStatus.ACCEPTED, RequestStatus.IN_PROGRESS])
    completed = mine.filter(status=RequestStatus.COMPLETED).count()

    return render(request, 'dashboard/provider.html', {
        'queue': queue, 'active': active[:8],
        'queue_count': queue.count(), 'active_count': active.count(),
        'completed_count': completed,
    })


def admin_dashboard(request):
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)

    counts = {
        'patients': User.objects.filter(role=Role.PATIENT).count(),
        'doctors': User.objects.filter(role=Role.DOCTOR).count(),
        'labs': User.objects.filter(role=Role.LAB).count(),
        'pharmacists': User.objects.filter(role=Role.PHARMACIST).count(),
        'pending_users': User.objects.filter(is_approved=False, is_active=True).exclude(role=Role.ADMIN).count(),
        'total_requests': ServiceRequest.objects.count(),
        'open_requests': ServiceRequest.objects.filter(
            status__in=[RequestStatus.PENDING, RequestStatus.ACCEPTED, RequestStatus.IN_PROGRESS]
        ).count(),
        'today_requests': ServiceRequest.objects.filter(created_at__date=today).count(),
        'week_requests': ServiceRequest.objects.filter(created_at__gte=week_ago).count(),
    }

    by_type = list(ServiceRequest.objects.values('service_type').annotate(c=Count('id')).order_by('-c'))
    by_status = list(ServiceRequest.objects.values('status').annotate(c=Count('id')).order_by('-c'))

    # Daily activity (last 7 days)
    daily = []
    for i in range(7):
        d = (timezone.now() - timedelta(days=6 - i)).date()
        daily.append({
            'date': d.strftime('%a'),
            'requests': ServiceRequest.objects.filter(created_at__date=d).count(),
            'logins': ActivityLog.objects.filter(action='login', created_at__date=d).count(),
        })

    pending = User.objects.filter(is_approved=False, is_active=True).exclude(role=Role.ADMIN)[:6]
    recent_logs = ActivityLog.objects.select_related('user').all()[:10]
    recent_requests = ServiceRequest.objects.select_related('patient', 'provider')[:8]

    return render(request, 'dashboard/admin.html', {
        'counts': counts,
        'by_type': by_type,
        'by_status': by_status,
        'daily': daily,
        'pending_users': pending,
        'recent_logs': recent_logs,
        'recent_requests': recent_requests,
    })


@admin_required
def admin_users(request):
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()

    qs = User.objects.exclude(role=Role.ADMIN).order_by('-created_at')
    if role:
        qs = qs.filter(role=role)
    if status == 'pending':
        qs = qs.filter(is_approved=False, is_active=True)
    elif status == 'approved':
        qs = qs.filter(is_approved=True)
    elif status == 'rejected':
        qs = qs.filter(is_active=False)
    if q:
        qs = qs.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    return render(request, 'dashboard/admin_users.html', {
        'users': qs[:200], 'role_filter': role, 'status_filter': status, 'q': q,
        'roles': Role.choices,
    })


@admin_required
def admin_user_action(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    action = request.POST.get('action')

    if action == 'approve':
        target.approve(by_user=request.user)
        Notification.objects.create(
            user=target, title='Account approved',
            body='Your account has been approved. You now have full access to HEALTHAPP.',
            category='account',
        )
        ActivityLog.objects.create(user=request.user, action='approve_user',
                                    description=f'Approved {target.email}')
        messages.success(request, f'{target.display_name} approved.')

    elif action == 'reject':
        reason = request.POST.get('reason', '')
        target.reject(reason=reason, by_user=request.user)
        ActivityLog.objects.create(user=request.user, action='reject_user',
                                    description=f'Rejected {target.email}: {reason}')
        messages.warning(request, f'{target.display_name} rejected.')

    elif action == 'reactivate':
        target.is_active = True
        target.save(update_fields=['is_active'])
        messages.success(request, f'{target.display_name} reactivated.')

    return redirect('dashboard:admin_users')


@admin_required
def admin_requests(request):
    qs = ServiceRequest.objects.select_related('patient', 'provider').order_by('-created_at')
    status = request.GET.get('status', '')
    stype = request.GET.get('type', '')
    if status: qs = qs.filter(status=status)
    if stype: qs = qs.filter(service_type=stype)
    return render(request, 'dashboard/admin_requests.html', {
        'requests': qs[:200], 'status': status, 'type': stype,
        'statuses': RequestStatus.choices, 'types': ServiceType.choices,
    })


@admin_required
def admin_logs(request):
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')[:300]
    return render(request, 'dashboard/admin_logs.html', {'logs': logs})
