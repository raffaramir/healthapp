from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from .models import ServiceRequest, Appointment, RequestStatus
from .serializers import ServiceRequestSerializer, AppointmentSerializer


class ServiceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ServiceRequest.objects.select_related('patient', 'provider')
        if user.is_admin_role:
            return qs
        if user.is_patient:
            return qs.filter(patient=user)
        type_map = {
            Role.DOCTOR: ['doctor_home', 'consultation'],
            Role.LAB: ['lab_home'],
            Role.PHARMACIST: ['pharmacy_order'],
        }
        allowed = type_map.get(user.role, [])
        return qs.filter(Q(provider=user) | Q(provider__isnull=True, service_type__in=allowed))

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        sr = self.get_object()
        if sr.status != RequestStatus.PENDING or request.user.is_patient:
            return Response({'detail': 'Cannot accept'}, status=400)
        sr.provider = request.user
        sr.status = RequestStatus.ACCEPTED
        sr.save()
        return Response(self.get_serializer(sr).data)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_role:
            return Appointment.objects.all()
        return Appointment.objects.filter(
            Q(service_request__patient=user) | Q(service_request__provider=user)
        )
