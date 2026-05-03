from django.contrib import admin
from .models import LabProfile


@admin.register(LabProfile)
class LabProfileAdmin(admin.ModelAdmin):
    list_display = ('lab_name', 'user', 'license_number', 'is_available')
    search_fields = ('lab_name', 'user__email', 'license_number')
    list_filter = ('is_available',)
