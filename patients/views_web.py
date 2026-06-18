from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Patient
from .forms import PatientForm

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    
    def get_queryset(self):
        return Patient.objects.filter(clinic=self.request.user.clinic, is_archived=False).order_by('-created_at')

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'
    lookup_field = 'id'

    def get_queryset(self):
        return Patient.objects.filter(clinic=self.request.user.clinic)

class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patients_web:patient-list')

    def form_valid(self, form):
        form.instance.clinic = self.request.user.clinic
        messages.success(self.request, "Patient created successfully.")
        return super().form_valid(form)

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    
    def get_queryset(self):
        return Patient.objects.filter(clinic=self.request.user.clinic)
    
    def get_success_url(self):
        return reverse_lazy('patients_web:patient-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Patient updated successfully.")
        return super().form_valid(form)

class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patients_web:patient-list')

    def get_queryset(self):
        return Patient.objects.filter(clinic=self.request.user.clinic)

    def form_valid(self, form):
        messages.success(self.request, "Patient deleted successfully.")
        return super().form_valid(form)
