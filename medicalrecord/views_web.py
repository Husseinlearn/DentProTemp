from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import MedicalRecord, Attachment
from .forms import MedicalRecordForm, AttachmentForm

class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = 'medicalrecord/record_list.html'
    context_object_name = 'records'

class MedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = 'medicalrecord/record_detail.html'
    context_object_name = 'record'

class MedicalRecordCreateView(CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'medicalrecord/record_form.html'
    success_url = reverse_lazy('medicalrecord_web:record-list')

    def form_valid(self, form):
        messages.success(self.request, "Medical Record created successfully.")
        return super().form_valid(form)

class MedicalRecordUpdateView(UpdateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'medicalrecord/record_form.html'
    
    def get_success_url(self):
        return reverse_lazy('medicalrecord_web:record-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Medical Record updated successfully.")
        return super().form_valid(form)

class MedicalRecordDeleteView(DeleteView):
    model = MedicalRecord
    template_name = 'medicalrecord/record_confirm_delete.html'
    success_url = reverse_lazy('medicalrecord_web:record-list')

    def form_valid(self, form):
        messages.success(self.request, "Medical Record deleted successfully.")
        return super().form_valid(form)

class AttachmentCreateView(CreateView):
    model = Attachment
    form_class = AttachmentForm
    template_name = 'medicalrecord/attachment_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        record_id = self.request.GET.get('record')
        if record_id:
            initial['medical_record'] = record_id
        return initial

    def get_success_url(self):
        return reverse_lazy('medicalrecord_web:record-detail', kwargs={'pk': self.object.medical_record.pk})

    def form_valid(self, form):
        messages.success(self.request, "تم تحميل المرفق بنجاح.")
        return super().form_valid(form)
