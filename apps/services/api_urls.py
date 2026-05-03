from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'requests', api_views.ServiceRequestViewSet, basename='servicerequest')
router.register(r'appointments', api_views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
