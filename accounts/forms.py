from django import forms
from .models import CustomUser, Doctor, UserProfile

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['user', 'specialization', 'license_number', 'revenue_share']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'revenue_share': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
