from django import forms
from apps.accounts.forms import StyledFormMixin
from .models import ServiceRequest, ServiceType, Review


class DoctorHomeRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'address', 'preferred_datetime', 'urgency']
        widgets = {
            'preferred_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class LabHomeRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'address', 'preferred_datetime', 'urgency']
        widgets = {
            'preferred_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tests requested (e.g. CBC, glucose, lipid panel)'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class PharmacyOrderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['title', 'prescription_text', 'prescription_image', 'address',
                  'preferred_datetime', 'urgency']
        widgets = {
            'preferred_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'prescription_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List medicines needed, or upload prescription image'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class ConsultationRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'urgency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your symptoms or questions...'}),
        }


class ProviderResponseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['estimated_cost', 'provider_notes']
        widgets = {
            'provider_notes': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(StyledFormMixin, forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}


SERVICE_FORM_MAP = {
    ServiceType.DOCTOR_HOME: ('Doctor home visit', DoctorHomeRequestForm),
    ServiceType.LAB_HOME: ('Lab technician at home', LabHomeRequestForm),
    ServiceType.PHARMACY_ORDER: ('Pharmacy order', PharmacyOrderForm),
    ServiceType.CONSULTATION: ('Online consultation', ConsultationRequestForm),
}
