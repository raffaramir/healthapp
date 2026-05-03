"""HEALTHAPP URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.dashboard.views import landing


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),

    # i18n: language switcher endpoint (set_language)
    path('i18n/', include('django.conf.urls.i18n')),

    # PWA — manifest + service worker must be served at root scope.
    path(
        'manifest.webmanifest',
        TemplateView.as_view(
            template_name='pwa/manifest.webmanifest',
            content_type='application/manifest+json',
        ),
        name='pwa_manifest',
    ),
    path(
        'sw.js',
        TemplateView.as_view(
            template_name='pwa/sw.js',
            content_type='application/javascript',
        ),
        name='pwa_sw',
    ),
    path(
        'offline/',
        TemplateView.as_view(template_name='pwa/offline.html'),
        name='pwa_offline',
    ),

    # App URLs (web)
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('chat/', include('apps.chat.urls', namespace='chat')),
    path('patients/', include('apps.patients.urls', namespace='patients')),
    path('doctors/', include('apps.doctors.urls', namespace='doctors')),
    path('labs/', include('apps.labs.urls', namespace='labs')),
    path('pharmacy/', include('apps.pharmacy.urls', namespace='pharmacy')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),

    # API endpoints
    path('api/v1/accounts/', include('apps.accounts.api_urls')),
    path('api/v1/services/', include('apps.services.api_urls')),
    path('api/v1/chat/', include('apps.chat.api_urls')),
    path('api/v1/notifications/', include('apps.notifications.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "HEALTHAPP Administration"
admin.site.site_title = "HEALTHAPP Admin"
admin.site.index_title = "Healthcare Platform Management"
