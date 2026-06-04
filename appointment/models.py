from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from patients.models import Patient
from accounts.models import Doctor
# Create your models here.
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
        ('معلق', 'معلق'),
        ('مؤكد', 'مؤكد'),
        ('منجز', 'منجز'),
        ('ملغي', 'ملغي'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.patient} with {self.doctor} on {self.date} at {self.time}"
