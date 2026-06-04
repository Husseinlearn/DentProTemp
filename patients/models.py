from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Lower
# Create your models here.

# --------------------------------------------------------------------
# Patient Model: جدول  المرضى 
# --------------------------------------------------------------------
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(max_length=10,
    choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('انثى', 'أنثى'), 
        ('ذكر', 'ذكر'), 
        ('غير ذلك', 'غير ذلك')
        ],
        null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone"), unique=True)
    email = models.EmailField(verbose_name=_("Email"), null=True, blank=True, unique=True)
    address = models.TextField(verbose_name=_("Address"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_archived = models.BooleanField(default=False, verbose_name=_("Archived"))

    # علاقات M2M عبر جداول ربط (للاستعلام السهل)
    diseases = models.ManyToManyField(
        "patients.Disease",
        through="patients.PatientDisease",
        related_name="patients",
        blank=True,
        verbose_name=_("Chronic Diseases")
    )
    allergies = models.ManyToManyField(
        "patients.Medication",
        through="patients.PatientAllergy",
        related_name="patients",
        blank=True,
        verbose_name=_("Drug Allergies")
    )

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_archived"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
# --------------------------------------------------------------------
# Disease Model: قاموس الأمراض المزمنة (اسم + تأثير على طب الأسنان)
# --------------------------------------------------------------------
class Disease(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Disease Name"))
    dental_impact = models.TextField(blank=True, null=True, verbose_name=_("Dental Impact"))
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Chronic Disease")
        verbose_name_plural = _("Chronic Diseases")
        ordering = ["name"]
        # فريد بدون حساسية حالة الأحرف (PostgreSQL + Django 3.2+)
        constraints = [
            models.UniqueConstraint(Lower('name'), name='uniq_disease_name_ci'),
        ]
        indexes = [
            models.Index(Lower('name'), name='idx_disease_name_ci'),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name



# --------------------------------------------------------------------
# PatientDisease Model: ربط المرضى بالأمراض
# --------------------------------------------------------------------
class PatientDisease(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="patient_diseases"
    )
    # PROTECT لمنع حذف المرض وهو مرتبط بمرضى
    disease = models.ForeignKey(
        Disease, on_delete=models.PROTECT, related_name="patient_disease_links"
    )
    diagnosed_at = models.DateField(verbose_name=_("Diagnosed At"), null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        db_table = "PATIENT_DISEASES"
        verbose_name = _("Patient Disease")
        verbose_name_plural = _("Patient Diseases")
        ordering = ["-created_at"]  # ترتيب حسب تاريخ الإنشاء
        constraints = [
            models.UniqueConstraint(fields=('patient', 'disease'), name='uniq_patient_disease'),
        ]
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['disease']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.disease}"

# --------------------------------------------------------------------
# Medication Model: قاموس الأدوية (اسم + تأثير على طب الأسنان)
# --------------------------------------------------------------------
class Medication(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Medication Name"))
    dental_impact = models.TextField(blank=True, null=True, verbose_name=_("Dental Impact"))
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Medication")
        verbose_name_plural = _("Medications")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower('name'), name='uniq_medication_name_ci'),
        ]
        indexes = [
            models.Index(Lower('name'), name='idx_medication_name_ci'),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name



# --------------------------------------------------------------------
# PatientAllergy Model: ربط المرضى بالحساسية من الأدوية
# --------------------------------------------------------------------
class PatientAllergy(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="patient_allergies"
    )
    # PROTECT لمنع حذف الدواء وهو مرتبط بحساسية مرضى
    medication = models.ForeignKey(
        Medication, on_delete=models.PROTECT, related_name="patient_allergy_links"
    )
    allergic_reaction = models.TextField(blank=True, null=True, verbose_name=_("Allergic Reaction"))
    diagnosed_at = models.DateField(verbose_name=_("Diagnosed At"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        db_table = "PATIENT_ALLERGIES"
        verbose_name = _("Patient Allergy")
        verbose_name_plural = _("Patient Allergies")
        ordering = ["-created_at"] # ترتيب حسب تاريخ الإنشاء
        constraints = [
            models.UniqueConstraint(fields=('patient', 'medication'), name='uniq_patient_medication'),
        ]
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['medication']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.medication}"