from django import forms
from .models import MedicalRecord, Attachment, Medication, PrescribedMedication

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.clinic:
            self.fields['patient'].queryset = self.fields['patient'].queryset.filter(clinic=user.clinic, is_archived=False)

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['medical_record', 'type', 'file', 'description']
        widgets = {
            'medical_record': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.clinic:
            self.fields['medical_record'].queryset = self.fields['medical_record'].queryset.filter(patient__clinic=user.clinic)

class PrescribedMedicationForm(forms.ModelForm):
    class Meta:
        model = PrescribedMedication
        fields = ['clinical_exam', 'medication', 'times_per_day', 'dose_unit', 'number_of_days', 'notes']
        widgets = {
            'clinical_exam': forms.Select(attrs={'class': 'form-select'}),
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'times_per_day': forms.TextInput(attrs={'class': 'form-control'}),
            'dose_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_days': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
