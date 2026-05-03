from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api_views

router = DefaultRouter()
router.register(r'users', api_views.UserViewSet, basename='user')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', api_views.MeView.as_view(), name='me'),
    path('approve/<int:user_id>/', api_views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', api_views.reject_user, name='reject_user'),
    path('', include(router.urls)),
]
