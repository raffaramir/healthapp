"""Authentication and registration forms."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Role


class StyledFormMixin:
    """Apply glass UI classes to every field."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-input'
            if isinstance(field.widget, forms.Select):
                css = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                css = 'form-textarea'
            elif isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check'
            elif isinstance(field.widget, forms.ClearableFileInput):
                css = 'form-file'
            field.widget.attrs.setdefault('class', css)
            if field.label:
                field.widget.attrs.setdefault('placeholder', field.label)


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.EmailField(label='Email')


class BaseRegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_image']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True, role=Role.PATIENT):
        user = super().save(commit=False)
        user.role = role
        user.set_password(self.cleaned_data['password1'])
        user.is_active = True  # they can login but features locked until approved
        user.is_approved = False
        if commit:
            user.save()
        return user


class PatientRegisterForm(BaseRegisterForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), required=True, label='Date of birth'
    )
    place_of_birth = forms.CharField(max_length=120, required=True, label='Place of birth')

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=commit, role=Role.PATIENT)
        if commit:
            from apps.patients.models import PatientProfile
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                place_of_birth=self.cleaned_data['place_of_birth'],
            )
        return user


class DoctorRegisterForm(BaseRegisterForm):
    specialty = forms.CharField(max_length=120, required=True)
    license_number = forms.CharField(max_length=80, required=True)
    professional_card = forms.ImageField(required=False, label='Professional card (image)')
    years_of_experience = forms.IntegerField(min_value=0, required=False, initial=0)

    def save(self, commit=True):
        user = super().save(commit=commit, role=Role.DOCTOR)
        if commit:
            from apps.doctors.models import DoctorProfile
            DoctorProfile.objects.create(
                user=user,
                specialty=self.cleaned_data['specialty'],
                license_number=self.cleaned_data['license_number'],
                professional_card=self.cleaned_data.get('professional_card'),
                years_of_experience=self.cleaned_data.get('years_of_experience') or 0,
            )
        return user


class LabRegisterForm(BaseRegisterForm):
    lab_name = forms.CharField(max_length=160, required=True)
    license_number = forms.CharField(max_length=80, required=True)
    professional_card = forms.ImageField(required=False)

    def save(self, commit=True):
        user = super().save(commit=commit, role=Role.LAB)
        if commit:
            from apps.labs.models import LabProfile
            LabProfile.objects.create(
                user=user,
                lab_name=self.cleaned_data['lab_name'],
                license_number=self.cleaned_data['license_number'],
                professional_card=self.cleaned_data.get('professional_card'),
            )
        return user


class PharmacistRegisterForm(BaseRegisterForm):
    pharmacy_name = forms.CharField(max_length=160, required=True)
    license_number = forms.CharField(max_length=80, required=True)
    professional_card = forms.ImageField(required=False)

    def save(self, commit=True):
        user = super().save(commit=commit, role=Role.PHARMACIST)
        if commit:
            from apps.pharmacy.models import PharmacistProfile
            PharmacistProfile.objects.create(
                user=user,
                pharmacy_name=self.cleaned_data['pharmacy_name'],
                license_number=self.cleaned_data['license_number'],
                professional_card=self.cleaned_data.get('professional_card'),
            )
        return user


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address', 'profile_image']
