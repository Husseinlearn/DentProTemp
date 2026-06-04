from django.contrib import admin
from .models import Patient, Disease, Medication, PatientDisease, PatientAllergy

class PatientDiseaseInline(admin.TabularInline):
    model = PatientDisease
    extra = 1
    autocomplete_fields = ["disease"]

class PatientAllergyInline(admin.TabularInline):
    model = PatientAllergy
    extra = 1
    autocomplete_fields = ["medication"]

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "is_archived", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("is_archived",)
    inlines = [PatientDiseaseInline, PatientAllergyInline]

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
