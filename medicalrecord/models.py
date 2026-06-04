from django.db import models
from django.utils.translation import gettext_lazy as _
from patients.models import Patient, Disease
from accounts.models import Doctor
from appointment.models import Appointment
# Create your models here.

class MedicalRecord(models.Model):
    """السجل الطبي الرئيسي لكل مريض"""
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='medical_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Medical Record")
        verbose_name_plural = _("Medical Records")

    def __str__(self):
        return f"Medical Record - {self.patient}"





class Attachment(models.Model):
    """المرفقات المرتبطة بالسجل الطبي أو الفحوصات"""
    class AttachmentType(models.TextChoices):
        XRAY = "xray", _("X-Ray")
        REPORT = "report", _("Report")
        IMAGE = "image", _("Image")
        OTHER = "other", _("Other")

    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='medical_attachments/')
    type = models.CharField(max_length=20, choices=AttachmentType.choices, default=AttachmentType.OTHER)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")

    def __str__(self):
        return f"{self.get_type_display()} - {self.medical_record.patient}"

class Medication(models.Model):
    """تعريف دواء متاح في النظام"""
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Medication Name"))
    description = models.TextField(blank=True, null=True)
    default_dose_unit = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Default Dose Unit"))  # مثال: حبة، كبسولة
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Medication")
        verbose_name_plural = _("Medications")
        ordering = ["name"]
    def __str__(self):
        return self.name



class PrescribedMedication(models.Model):
    """
    وصفة طبية مرتبطة بدواء ,الفحص السريري 
    """
    clinical_exam = models.ForeignKey(
        "procedures.ClinicalExam", 
        on_delete=models.CASCADE,
        related_name="prescribed_medications",
        verbose_name=_("Clinical Exam")
        )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name=_("Medication")
        )
    times_per_day = models.CharField(max_length=60,null=True,blank=True,verbose_name=_("Times Per Day"))
    dose_unit = models.CharField(max_length=50, verbose_name=_("Dose Unit"))
    number_of_days = models.CharField(max_length=60,null=True,blank=True,verbose_name=_("Number Of Days"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    prescribed_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name=_("Prescribed By"))
    prescribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Prescribed At"))
    class Meta:
        verbose_name = _("Prescribed Medication")
        verbose_name_plural = _("Prescribed Medications")
        ordering = ["-prescribed_at"]
        

    def __str__(self):
        return f"{self.medication.name} for {self.clinical_exam.patient}"


# -------------------------------------------------
# 3) حزمة أدوية مرتبطة بمرض مزمن (Disease)
# -------------------------------------------------
class MedicationPackage(models.Model):
    """
    حزمة أدوية جاهزة لمرض/حالة مزمنة محدّدة (مثال: التهاب اللثة)
    تُستخدم كقالب لتوليد عناصر وصفة داخل الفحص السريري.
    """
    name = models.CharField(max_length=255, verbose_name=_("Package Name"))
    disease = models.ForeignKey(
        Disease, on_delete=models.PROTECT, related_name="medication_packages",null=True, verbose_name=_("Disease")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Medication Package")
        verbose_name_plural = _("Medication Packages")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["disease"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.disease})"


# -------------------------------------------------
# 4) عناصر الحزمة: دواء + جرعات ومدّة افتراضية
# -------------------------------------------------
class MedicationPackageItem(models.Model):
    package = models.ForeignKey(
        MedicationPackage, on_delete=models.CASCADE, related_name="items", verbose_name=_("Package")
    )
    medication = models.ForeignKey(
        Medication, on_delete=models.PROTECT, related_name="package_items", verbose_name=_("Medication")
    )
    times_per_day = models.CharField(max_length=60,null=True,blank=True, verbose_name=_("Times Per Day"))
    dose_unit = models.CharField(max_length=50, verbose_name=_("Dose Unit"))
    number_of_days = models.CharField(max_length=60,null=True,blank=True, verbose_name=_("Number Of Days"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Medication Package Item")
        verbose_name_plural = _("Medication Package Items")
        unique_together = ("package", "medication")
        

    def __str__(self):
        return f"{self.medication} ×{self.times_per_day}/day for {self.number_of_days}d"


# -------------------------------------------------
# 5) سجل تطبيق الحزمة على فحص سريري (Audit)
# -------------------------------------------------
class AppliedMedicationPackage(models.Model):
    """
    أثر التطبيق: متى ولمن طُبّقت الحزمة ومن الطبيب وبأي نمط.
    لا تُخزّن الأدوية نفسها هنا؛ الأدوية الفعلية تُنشأ في PrescribedMedication.
    """
    MODE_APPEND = "append"
    MODE_REPLACE = "replace"
    MODE_CHOICES = (
        (MODE_APPEND, "append"),
        (MODE_REPLACE, "replace"),
    )

    clinical_exam = models.ForeignKey(
        "procedures.ClinicalExam",
        on_delete=models.CASCADE,
        related_name="applied_medication_packages",
        verbose_name=_("Clinical Exam"),
    )
    package = models.ForeignKey(
        MedicationPackage, on_delete=models.PROTECT, verbose_name=_("Medication Package")
    )
    prescribed_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name=_("Prescribed By"))
    prescribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Applied At"))
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_APPEND, verbose_name=_("Mode"))

    class Meta:
        verbose_name = _("Applied Medication Package")
        verbose_name_plural = _("Applied Medication Packages")
        ordering = ["-prescribed_at"]
        indexes = [
            models.Index(fields=["mode"]),
            models.Index(fields=["clinical_exam"]),
            models.Index(fields=["package"]),
        ]

    def __str__(self):
        return f"Applied {self.package} to exam #{self.clinical_exam_id} ({self.mode})"
    

class PatientPrescriptionReport(Patient):
    class Meta:
        proxy = True
        verbose_name = "تقرير وصفات المريض"
        verbose_name_plural = "تقارير وصفات المرضى"