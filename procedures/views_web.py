from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ClinicalExam, DentalProcedure
from .forms import ClinicalExamForm, DentalProcedureForm

class ClinicalExamListView(LoginRequiredMixin, ListView):
    model = ClinicalExam
    template_name = 'procedures/clinicalexam_list.html'
    context_object_name = 'exams'

class ClinicalExamDetailView(LoginRequiredMixin, DetailView):
    model = ClinicalExam
    template_name = 'procedures/clinicalexam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procedures'] = DentalProcedure.objects.filter(is_active=True).select_related('category')
        return context

class ClinicalExamCreateView(LoginRequiredMixin, CreateView):
    model = ClinicalExam
    form_class = ClinicalExamForm
    template_name = 'procedures/clinicalexam_form.html'
    success_url = reverse_lazy('procedures_web:exam-list')

    def form_valid(self, form):
        messages.success(self.request, "Clinical Exam created successfully.")
        return super().form_valid(form)

class ClinicalExamUpdateView(LoginRequiredMixin, UpdateView):
    model = ClinicalExam
    form_class = ClinicalExamForm
    template_name = 'procedures/clinicalexam_form.html'
    
    def get_success_url(self):
        return reverse_lazy('procedures_web:exam-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Clinical Exam updated successfully.")
        return super().form_valid(form)

class ClinicalExamDeleteView(LoginRequiredMixin, DeleteView):
    model = ClinicalExam
    template_name = 'procedures/clinicalexam_confirm_delete.html'
    success_url = reverse_lazy('procedures_web:exam-list')

    def form_valid(self, form):
        messages.success(self.request, "Clinical Exam deleted successfully.")
        return super().form_valid(form)
