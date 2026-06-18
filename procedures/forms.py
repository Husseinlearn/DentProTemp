from django import forms
from .models import ClinicalExam, DentalProcedure, ProcedureCategory

class ClinicalExamForm(forms.ModelForm):
    class Meta:
        model = ClinicalExam
        fields = ['patient', 'doctor', 'appointment', 'complaint', 'medical_advice', 'prescription_notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescription_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        from django.db.models import Q
        from appointment.models import Appointment
        
        if user and user.clinic:
            self.fields['patient'].queryset = self.fields['patient'].queryset.filter(clinic=user.clinic, is_archived=False)
            self.fields['doctor'].queryset = self.fields['doctor'].queryset.filter(user__clinic=user.clinic, user__is_archived=False)
            
            today = timezone.localdate()
            query = Q(date=today, clinic=user.clinic)
            
            # If editing an existing instance, preserve the currently selected appointment
            if self.instance and self.instance.pk and self.instance.appointment:
                query = query | Q(pk=self.instance.appointment.pk)
                
            self.fields['appointment'].queryset = Appointment.objects.filter(query)

class DentalProcedureForm(forms.ModelForm):
    class Meta:
        model = DentalProcedure
        fields = ['category', 'name', 'description', 'default_price', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'default_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
