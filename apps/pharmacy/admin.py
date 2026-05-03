from django.contrib import admin
from .models import PharmacistProfile, PharmacyProduct


@admin.register(PharmacistProfile)
class PharmacistProfileAdmin(admin.ModelAdmin):
    list_display = ('pharmacy_name', 'user', 'license_number', 'is_open')
    search_fields = ('pharmacy_name', 'user__email', 'license_number')


@admin.register(PharmacyProduct)
class PharmacyProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'pharmacy', 'price', 'in_stock', 'requires_prescription')
    list_filter = ('in_stock', 'requires_prescription')
    search_fields = ('name', 'pharmacy__pharmacy_name')
