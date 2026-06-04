from django.contrib import admin
from . models import ClinicalExam
from django.contrib import admin
from .models import (
    ClinicalExam, ProcedureCategory, DentalProcedure,
    Toothcode, Procedure, ProcedureToothcode,ClinicalExamItem
)
# from medicalrecord.admin import PrescribedMedicationInline
# Register your models here.


# @admin.register(ClinicalExam)
# class ClinicalExamAdmin(admin.ModelAdmin):
#     list_display = ('id', 'patient', 'doctor', 'appointment', 'created_at')
#     search_fields = ('patient__name', 'doctor__name', 'complaint')
#     list_filter = ('doctor', 'created_at')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at',)
    
#     def has_add_permission(self, request):
#         return True
    



class ProcedureToothcodeInline(admin.TabularInline):
    model = ProcedureToothcode
    extra = 0
    autocomplete_fields = ["toothcode", "performed_by"]

@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ["name", "clinical_exam", "category", "cost", "status", "created_at"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["name", "description", "clinical_exam__patient__first_name", "clinical_exam__patient__last_name"]
    autocomplete_fields = ["clinical_exam", "definition", "category"]
    inlines = [ProcedureToothcodeInline]

@admin.register(ClinicalExam)
class ClinicalExamAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "appointment", "created_at"]
    search_fields = ["patient__first_name", "patient__last_name", "doctor__first_name", "doctor__last_name"]
    autocomplete_fields = ["patient", "doctor", "appointment"]
    # inlines = [PrescribedMedicationInline]

@admin.register(ProcedureCategory)
class ProcedureCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]

@admin.register(DentalProcedure)
class DentalProcedureAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "default_price", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]
    autocomplete_fields = ["category"]

@admin.register(Toothcode)
class ToothcodeAdmin(admin.ModelAdmin):
    list_display = ["tooth_number", "tooth_type", "description", "created_at"]
    list_filter = ["tooth_type"]
    search_fields = ["tooth_number", "description"]

@admin.register(ProcedureToothcode)
class ProcedureToothcodeAdmin(admin.ModelAdmin):
    list_display = ["procedure", "toothcode", "performed_by", "performed_at"]
    list_filter = ["performed_by"]
    search_fields = ["procedure__name", "toothcode__tooth_number"]
    autocomplete_fields = ["procedure", "toothcode", "performed_by"]
@admin.register(ClinicalExamItem)
class ClinicalExamItemAdmin(admin.ModelAdmin):
    list_display = ["clinical_exam", "procedure", "toothcode", "performed_by", "created_at"]
    list_filter = ["performed_by", "procedure"]
    search_fields = ["clinical_exam__patient__first_name", "clinical_exam__patient__last_name", "procedure__name", "toothcode__tooth_number"]
    autocomplete_fields = ["clinical_exam", "procedure", "toothcode", "performed_by"]