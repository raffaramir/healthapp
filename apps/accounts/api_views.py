from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response

from .models import User, ActivityLog
from .serializers import UserSerializer
from .permissions import IsAdminRole


class MeView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        approved = self.request.query_params.get('approved')
        if role:
            qs = qs.filter(role=role)
        if approved in ('true', 'false'):
            qs = qs.filter(is_approved=(approved == 'true'))
        return qs


@api_view(['POST'])
@permission_classes([IsAdminRole])
def approve_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    user.approve(by_user=request.user)
    ActivityLog.objects.create(user=request.user, action='approve_user',
                               description=f'Approved {user.email}')

    from apps.notifications.models import Notification
    Notification.objects.create(
        user=user, title='Account approved',
        body='Your account has been approved. You now have full access to HEALTHAPP.',
        category='account',
    )
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAdminRole])
def reject_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    reason = request.data.get('reason', '')
    user.reject(reason=reason, by_user=request.user)
    ActivityLog.objects.create(user=request.user, action='reject_user',
                               description=f'Rejected {user.email}: {reason}')
    return Response(UserSerializer(user).data)
