from rest_framework import serializers
from .models import ServiceRequest, Appointment, Review


class ServiceRequestSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.display_name', read_only=True)
    provider_name = serializers.CharField(source='provider.display_name', read_only=True, default=None)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'patient', 'patient_name', 'provider', 'provider_name',
            'service_type', 'service_type_display', 'status', 'status_display',
            'urgency', 'title', 'description', 'address', 'preferred_datetime',
            'prescription_image', 'prescription_text',
            'estimated_cost', 'final_cost', 'provider_notes', 'rejection_reason',
            'accepted_at', 'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['patient', 'provider', 'status', 'accepted_at', 'completed_at']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
