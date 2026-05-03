from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile


@login_required
def doctor_list(request):
    qs = DoctorProfile.objects.filter(user__is_approved=True, is_available=True).select_related('user')
    specialty = request.GET.get('specialty', '').strip()
    if specialty:
        qs = qs.filter(specialty__icontains=specialty)
    return render(request, 'doctors/list.html', {'doctors': qs, 'specialty': specialty})


@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(
        DoctorProfile.objects.select_related('user'),
        pk=pk, user__is_approved=True
    )
    return render(request, 'doctors/detail.html', {'doctor': doctor})
