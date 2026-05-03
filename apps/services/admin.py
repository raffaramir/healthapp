from django.contrib import admin
from .models import ServiceRequest, Appointment, Review


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_type', 'patient', 'provider', 'status', 'urgency', 'created_at')
    list_filter = ('service_type', 'status', 'urgency')
    search_fields = ('title', 'patient__email', 'provider__email')
    readonly_fields = ('created_at', 'updated_at', 'accepted_at', 'completed_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('service_request', 'scheduled_at', 'duration_minutes', 'is_video')
    list_filter = ('is_video',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service_request', 'rating', 'created_at')
    list_filter = ('rating',)
