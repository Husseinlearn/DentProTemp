from django.contrib import admin
from .models import Appointment
# Register your models here.


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    ordering = ('-created_at',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)