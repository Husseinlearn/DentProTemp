from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment
from .forms import AppointmentForm

from django.utils import timezone
from django.db.models import Q

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointment/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Search Filter
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(doctor__user__first_name__icontains=search_query) |
                Q(doctor__user__last_name__icontains=search_query)
            )

        # 2. Status/Date Category Filter
        active_filter = self.request.GET.get('filter', 'all').strip()
        today = timezone.now().date()

        if active_filter == 'today':
            queryset = queryset.filter(date=today)
        elif active_filter == 'confirmed':
            queryset = queryset.filter(status__in=['confirmed', 'مؤكد'])
        elif active_filter == 'completed':
            queryset = queryset.filter(status__in=['completed', 'منجز'])
        elif active_filter == 'other':
            queryset = queryset.filter(status__in=['pending', 'cancelled', 'معلق', 'ملغي'])

        # 3. Sorting
        sort_by = self.request.GET.get('sort', 'newest').strip()
        if sort_by == 'oldest':
            queryset = queryset.order_by('date', 'time')
        else:
            queryset = queryset.order_by('-date', '-time')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Calculate counts across all categories
        base_queryset = Appointment.objects.all()
        context['count_all'] = base_queryset.count()
        context['count_today'] = base_queryset.filter(date=today).count()
        context['count_confirmed'] = base_queryset.filter(status__in=['confirmed', 'مؤكد']).count()
        context['count_completed'] = base_queryset.filter(status__in=['completed', 'منجز']).count()
        context['count_other'] = base_queryset.filter(status__in=['pending', 'cancelled', 'معلق', 'ملغي']).count()

        # Pass filters to maintain active state in UI
        context['active_filter'] = self.request.GET.get('filter', 'all')
        context['active_sort'] = self.request.GET.get('sort', 'newest')
        context['search_query'] = self.request.GET.get('search', '')

        return context

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'appointment/appointment_detail.html'
    context_object_name = 'appointment'
    lookup_field = 'id'
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return Appointment.objects.get(id=pk)
        return super().get_object(queryset)

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment/appointment_form.html'
    success_url = reverse_lazy('appointments_web:appointment-list')

    def form_valid(self, form):
        messages.success(self.request, "Appointment created successfully.")
        return super().form_valid(form)

class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment/appointment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('appointments_web:appointment-detail', kwargs={'pk': self.object.id})

    def get_object(self, queryset=None):
        return Appointment.objects.get(id=self.kwargs.get('pk'))

    def form_valid(self, form):
        messages.success(self.request, "Appointment updated successfully.")
        return super().form_valid(form)

class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'appointment/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointments_web:appointment-list')

    def get_object(self, queryset=None):
        return Appointment.objects.get(id=self.kwargs.get('pk'))

    def form_valid(self, form):
        messages.success(self.request, "Appointment deleted successfully.")
        return super().form_valid(form)
