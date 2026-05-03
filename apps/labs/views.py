from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import LabProfile


@login_required
def lab_list(request):
    qs = LabProfile.objects.filter(user__is_approved=True, is_available=True).select_related('user')
    return render(request, 'labs/list.html', {'labs': qs})


@login_required
def lab_detail(request, pk):
    lab = get_object_or_404(LabProfile.objects.select_related('user'), pk=pk, user__is_approved=True)
    return render(request, 'labs/detail.html', {'lab': lab})
