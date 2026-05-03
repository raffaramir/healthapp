from rest_framework import serializers
from .models import User, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'display_name',
            'role', 'role_display', 'phone', 'address', 'profile_image',
            'is_approved', 'is_email_verified', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_approved', 'is_email_verified', 'created_at', 'updated_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_email', 'action', 'description',
                  'ip_address', 'created_at']
