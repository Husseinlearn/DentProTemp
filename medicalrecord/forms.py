from django import forms
from .models import MedicalRecord, Attachment, Medication, PrescribedMedication

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
        }

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
