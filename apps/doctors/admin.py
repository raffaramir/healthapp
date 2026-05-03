from django.contrib import admin
from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'years_of_experience',
                    'is_available', 'rating_avg')
    list_filter = ('specialty', 'is_available')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'license_number')
