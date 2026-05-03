from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import PharmacistProfile


@login_required
def pharmacy_list(request):
    qs = PharmacistProfile.objects.filter(user__is_approved=True, is_open=True).select_related('user')
    return render(request, 'pharmacy/list.html', {'pharmacies': qs})


@login_required
def pharmacy_detail(request, pk):
    pharmacy = get_object_or_404(
        PharmacistProfile.objects.select_related('user'), pk=pk, user__is_approved=True
    )
    products = pharmacy.products.filter(in_stock=True)
    return render(request, 'pharmacy/detail.html', {'pharmacy': pharmacy, 'products': products})
