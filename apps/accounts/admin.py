from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, ActivityLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'role', 'badge_approval', 'is_active', 'created_at')
    list_filter = ('role', 'is_approved', 'is_active', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('email_verification_token', 'created_at', 'updated_at',
                       'approved_at', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone', 'address', 'profile_image')}),
        ('Role & Status', {'fields': ('role', 'is_approved', 'is_email_verified',
                                       'rejection_reason', 'approved_at', 'approved_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                     'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'first_name', 'last_name'),
        }),
    )

    actions = ['approve_selected', 'reject_selected']

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.get_full_name() or '-'

    @admin.display(description='Approval')
    def badge_approval(self, obj):
        if obj.is_approved:
            return format_html('<span style="color:#22C55E;font-weight:600">✓ Approved</span>')
        return format_html('<span style="color:#FFAA00;font-weight:600">⏳ Pending</span>')

    @admin.action(description='Approve selected accounts')
    def approve_selected(self, request, queryset):
        for user in queryset:
            user.approve(by_user=request.user)
        self.message_user(request, f'{queryset.count()} account(s) approved.')

    @admin.action(description='Reject selected accounts')
    def reject_selected(self, request, queryset):
        for user in queryset:
            user.reject(by_user=request.user)
        self.message_user(request, f'{queryset.count()} account(s) rejected.')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'action', 'description')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'user_agent', 'created_at')
