from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'status', 'reason']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.clinic:
            self.fields['patient'].queryset = self.fields['patient'].queryset.filter(clinic=user.clinic, is_archived=False)
            self.fields['doctor'].queryset = self.fields['doctor'].queryset.filter(user__clinic=user.clinic, user__is_archived=False)
