"""Custom User model with roles + email verification + admin approval."""
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    PATIENT = 'patient', _('Patient')
    DOCTOR = 'doctor', _('Doctor')
    LAB = 'lab', _('Lab Technician')
    PHARMACIST = 'pharmacist', _('Pharmacist')
    ADMIN = 'admin', _('Administrator')


class UserManager(BaseUserManager):
    """Email-based custom user manager."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('role', Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user — email is the unique identifier."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)

    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Approval / verification
    is_approved = models.BooleanField(
        default=False,
        help_text=_('Designates whether the user has been approved by an administrator.')
    )
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_users'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f'{self.get_full_name() or self.email} ({self.get_role_display()})'

    @property
    def display_name(self):
        return self.get_full_name() or self.email.split('@')[0]

    @property
    def is_patient(self): return self.role == Role.PATIENT

    @property
    def is_doctor(self): return self.role == Role.DOCTOR

    @property
    def is_lab(self): return self.role == Role.LAB

    @property
    def is_pharmacist(self): return self.role == Role.PHARMACIST

    @property
    def is_admin_role(self): return self.role == Role.ADMIN or self.is_superuser

    def approve(self, by_user=None):
        self.is_approved = True
        self.approved_at = timezone.now()
        self.approved_by = by_user
        self.save(update_fields=['is_approved', 'approved_at', 'approved_by'])

    def reject(self, reason='', by_user=None):
        self.is_approved = False
        self.rejection_reason = reason
        self.is_active = False
        self.approved_by = by_user
        self.save(update_fields=['is_approved', 'rejection_reason', 'is_active', 'approved_by'])


class ActivityLog(models.Model):
    """Audit log for important actions across the platform."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} @ {self.created_at:%Y-%m-%d %H:%M}'
