from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import (
    MedicalRecord,
    Attachment,
    Medication,
    PrescribedMedication,
    MedicationPackage,
    MedicationPackageItem,
    AppliedMedicationPackage,
    PatientPrescriptionReport,
)
from appointment.models import Appointment
from procedures.models import Procedure, ProcedureToothcode,ClinicalExam
from django.db.models import Count, Max

# ===========================
# Inlines
# ===========================
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ["file", "type", "description", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


class MedicationPackageItemInline(admin.TabularInline):
    model = MedicationPackageItem
    extra = 1
    autocomplete_fields = ["medication"]
    fields = ["medication", "times_per_day", "dose_unit", "number_of_days", "notes"]


# ===========================
# MedicalRecord Admin
# ===========================
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["patient", "created_at"]
    search_fields = ["patient__first_name", "patient__last_name", "patient__email"]
    readonly_fields = [
        "created_at", "updated_at",
        "patient_details",
        "patient_diseases_list",
        "patient_allergies_list",
        "appointment_history",
        "procedures_history",      
        "prescriptions_history",   
    ]
    fields = [
        "patient",
        "patient_details",
        "patient_diseases_list",
        "patient_allergies_list",
        "appointment_history",
        "procedures_history",      
        "prescriptions_history",  
        "created_at", "updated_at",
    ]
    inlines = [AttachmentInline]

    # --- تفاصيل المريض
    def patient_details(self, obj):
        if not obj or not obj.patient:
            return "-"
        p = obj.patient
        gender_display = getattr(p, "get_gender_display", None)
        gender_value = gender_display() if callable(gender_display) else (p.gender or "—")
        return format_html(
            "الاسم: {} {}<br>"
            "البريد: {}<br>"
            "الجنس: {}<br>"
            "الجوال: {}<br>"
            "العنوان: {}<br>"
            "تاريخ الميلاد: {}<br>"
            "المعرّف (UUID): {}",
            p.first_name or "—",
            p.last_name or "—",
            p.email or "—",
            gender_value,
            p.phone or "—",
            p.address or "—",
            getattr(p, "date_of_birth", "—") or "—",
            getattr(p, "id", "—"),
        )
    patient_details.short_description = "تفاصيل المريض"

    # --- الأمراض المزمنة (افترض related_name='patient_diseases')
    def patient_diseases_list(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        rel = getattr(obj.patient, "patient_diseases", None)
        if not rel:
            return "—"
        items = []
        for pd in rel.all():
            name = getattr(getattr(pd, "disease", None), "name", None) or getattr(pd, "disease_name", None) or "—"
            diagnosed = getattr(pd, "diagnosed_at", None) or "غير محدد"
            notes = getattr(pd, "notes", None) or ""
            items.append((f"{name} — {diagnosed} {('— '+notes) if notes else ''}",))
        return format_html_join("\n", "<div>• {}</div>", items) if items else "لا يوجد"
    patient_diseases_list.short_description = "الأمراض المزمنة"

    # --- حساسيّات الأدوية (افترض related_name='patient_allergies')
    def patient_allergies_list(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        rel = getattr(obj.patient, "patient_allergies", None)
        if not rel:
            return "—"
        items = []
        for pa in rel.all():
            med_name = getattr(getattr(pa, "medication", None), "name", None) or "—"
            severity = getattr(pa, "severity", None) or "—"
            notes = getattr(pa, "notes", None) or ""
            items.append((f"{med_name} — الشدة: {severity} {('— '+notes) if notes else ''}",))
        return format_html_join("\n", "<div>• {}</div>", items) if items else "لا يوجد"
    patient_allergies_list.short_description = "حساسيات الأدوية"

    # --- سجل المواعيد والفحوصات
    def appointment_history(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"
        appointments = (
            Appointment.objects
            .filter(patient=obj.patient)
            .select_related("doctor__user")
            .order_by("-date", "-time")
        )
        if not appointments.exists():
            return "لا توجد مواعيد"

        rows = []
        for appt in appointments:
            doctor_name = (
                appt.doctor.user.get_full_name()
                if getattr(appt, "doctor", None) and getattr(appt.doctor, "user", None)
                else "—"
            )
            status_display = appt.get_status_display() if hasattr(appt, "get_status_display") else (appt.status or "—")

            row = f"<b>📅 التاريخ:</b> {getattr(appt, 'date', '—')} - <b>🕒 الوقت:</b> {getattr(appt, 'time', '—')}<br>"
            row += f"<b>👨‍⚕️ الطبيب:</b> {doctor_name}<br>"
            row += f"<b>📌 الحالة:</b> {status_display}<br>"

            exam = getattr(appt, "clinical_exam", None)
            if exam:
                row += "<i>🔍 فحص سريري:</i><br>"
                row += f"&nbsp;&nbsp;- الشكوى: {getattr(exam, 'complaint', None) or '-'}<br>"
                row += f"&nbsp;&nbsp;- النصيحة: {getattr(exam, 'medical_advice', None) or '-'}<br>"
                row += f"&nbsp;&nbsp;- الإجراءات: {getattr(exam, 'planned_procedures', None) or '-'}<br>"
            else:
                row += "<i>⚠ لا يوجد فحص سريري لهذا الموعد</i><br>"

            rows.append(row)
        return format_html("<hr>".join(rows))
    appointment_history.short_description = "سجل المواعيد والفحوصات"

    # --- الإجراءات المنفّذة على أسنان المريض
    def procedures_history(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"

        qs = (
            Procedure.objects
            .filter(clinical_exam__patient=obj.patient)
            .select_related("clinical_exam__appointment", "definition", "clinical_exam__doctor__user")
            .order_by("-created_at")
        )

        if not qs.exists():
            return "لا توجد إجراءات مسجّلة"

        rows = []
        for proc in qs:
            # اسم الإجراء التعريفي
            proc_name = (
                getattr(getattr(proc, "dental_procedure", None), "name", None)
                or getattr(getattr(proc, "procedure", None), "name", None)
                or getattr(proc, "procedure_name", None)
                or "إجراء غير محدد"
            )

            # الأسنان المرتبطة
            teeth_parts = []
            try:
                tqs = (
                    ProcedureToothcode.objects
                    .filter(procedure=proc)
                    .select_related("toothcode")
                )
                for t in tqs:
                    tc = getattr(t, "toothcode", None)
                    code = (
                        getattr(tc, "code", None)
                        or getattr(tc, "number", None)
                        or getattr(tc, "name", None)
                    )
                    if code:
                        teeth_parts.append(str(code))
            except Exception:
                pass

            # fallback: علاقة مباشرة M2M إن وُجدت
            if not teeth_parts:
                rel = getattr(proc, "teeth", None)
                if rel is not None:
                    try:
                        for tc in rel.all():
                            code = (
                                getattr(tc, "code", None)
                                or getattr(tc, "number", None)
                                or getattr(tc, "name", None)
                            )
                            if code:
                                teeth_parts.append(str(code))
                    except Exception:
                        pass

            teeth_txt = ", ".join(teeth_parts) if teeth_parts else "—"

            # الطبيب
            performed_by = getattr(proc, "performed_by", None)
            doctor_name = (
                getattr(getattr(performed_by, "user", None), "get_full_name", lambda: None)()  # type: ignore
                if performed_by else None
            ) or "—"

            # الموعد
            appt = getattr(getattr(proc, "clinical_exam", None), "appointment", None)
            appt_date = getattr(appt, "date", None) or "—"
            appt_time = getattr(appt, "time", None) or "—"

            notes = getattr(proc, "notes", None) or "—"
            created_at = getattr(proc, "created_at", None) or "—"

            row = (
                f"<b>🧾 الإجراء:</b> {proc_name}<br>"
                f"<b>🦷 الأسنان:</b> {teeth_txt}<br>"
                f"<b>👨‍⚕️ الطبيب:</b> {doctor_name}<br>"
                f"<b>📅 الموعد:</b> {appt_date} — {appt_time}<br>"
                f"<b>📝 ملاحظات:</b> {notes}<br>"
                f"<b>⏱️ أُنشئ في:</b> {created_at}"
            )
            rows.append(row)

        return format_html("<hr>".join(rows))

    procedures_history.short_description = "الإجراءات المنفّذة"

    # --- الوصفات الطبية المصروفة (أدوية مفردة لكل فحص)
    def prescriptions_history(self, obj):
        if not obj or not obj.patient:
            return "لا يوجد مريض مرتبط"

        qs = (
            PrescribedMedication.objects
            .filter(clinical_exam__patient=obj.patient)
            .select_related(
                "medication",
                "prescribed_by__user",
                "clinical_exam__appointment",
            )
            .order_by("-prescribed_at")
        )

        if not qs.exists():
            return "لا توجد وصفات مصروفة"

        rows = []
        for pm in qs:
            med_name = getattr(getattr(pm, "medication", None), "name", None) or "—"
            times_per_day = getattr(pm, "times_per_day", None)
            dose_unit = getattr(pm, "dose_unit", None) or "—"
            number_of_days = getattr(pm, "number_of_days", None)
            notes = getattr(pm, "notes", None) or "—"

            prescriber = getattr(pm, "prescribed_by", None)
            prescriber_name = (
                getattr(getattr(prescriber, "user", None), "get_full_name", lambda: None)()  # type: ignore
                if prescriber else None
            ) or "—"

            prescribed_at = getattr(pm, "prescribed_at", None) or "—"

            appt = getattr(getattr(pm, "clinical_exam", None), "appointment", None)
            appt_date = getattr(appt, "date", None) or "—"
            appt_time = getattr(appt, "time", None) or "—"

            row = (
                f"<b>💊 الدواء:</b> {med_name}<br>"
                f"<b>⏰ الجرعات/اليوم:</b> {times_per_day if times_per_day is not None else '—'}<br>"
                f"<b>🧪 وحدة الجرعة:</b> {dose_unit}<br>"
                f"<b>📆 عدد الأيام:</b> {number_of_days if number_of_days is not None else '—'}<br>"
                f"<b>📝 ملاحظات:</b> {notes}<br>"
                f"<b>👨‍⚕️ الموصي:</b> {prescriber_name}<br>"
                f"<b>🕒 وقت الصرف:</b> {prescribed_at}<br>"
                f"<b>📅 الموعد:</b> {appt_date} — {appt_time}"
            )
            rows.append(row)

        return format_html("<hr>".join(rows))

    prescriptions_history.short_description = "الوصفات الطبية المصروفة"


# ===========================
# Attachment
# ===========================
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["type", "medical_record", "uploaded_at"]
    search_fields = ["medical_record__patient__first_name", "medical_record__patient__last_name"]
    list_filter = ["type", "uploaded_at"]
    raw_id_fields = ["medical_record"]


# ===========================
# Medication
# ===========================
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ["name", "default_dose_unit", "is_active"]
    search_fields = ["name"]
    list_filter = ["is_active"]


# ===========================
# PrescribedMedication
# ===========================
@admin.register(PrescribedMedication)
class PrescribedMedicationAdmin(admin.ModelAdmin):
    list_display = [
        "medication", "clinical_exam",
        "times_per_day", "dose_unit", "number_of_days",
        "prescribed_by", "prescribed_at",
    ]
    search_fields = [
        "medication__name",
        "clinical_exam__patient__first_name",
        "clinical_exam__patient__last_name",
    ]
    list_filter = ["prescribed_by", "prescribed_at"]
    raw_id_fields = ["clinical_exam", "medication", "prescribed_by"]
    # def has_module_permission(self, request):
    #     # يمنع ظهور التطبيق في فهرس الأدمن
    #     return False

# ===========================
# MedicationPackage (+ items)
# ===========================
@admin.register(MedicationPackage)
class MedicationPackageAdmin(admin.ModelAdmin):
    list_display = ["name", "disease", "is_active", "created_at", "items_count"]
    search_fields = ["name", "disease__name"]
    list_filter = ["is_active", "disease"]
    inlines = [MedicationPackageItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "عدد الأدوية"


# ===========================
# AppliedMedicationPackage
# ===========================
@admin.register(AppliedMedicationPackage)
class AppliedMedicationPackageAdmin(admin.ModelAdmin):
    list_display = ["package", "clinical_exam", "prescribed_by", "mode", "prescribed_at"]
    list_filter = ["mode", "prescribed_by", "prescribed_at", "package__disease"]
    search_fields = [
        "package__name",
        "package__disease__name",
        "clinical_exam__patient__first_name",
        "clinical_exam__patient__last_name",
    ]
    raw_id_fields = ["clinical_exam", "package", "prescribed_by"]


class PrescribedMedicationInline(admin.TabularInline):
    model = PrescribedMedication
    extra = 1
    autocomplete_fields = ["medication"]
    fields = ["medication", "times_per_day", "dose_unit", "number_of_days", "notes", "prescribed_by", "prescribed_at"]
    readonly_fields = ["prescribed_at"]

# # @admin.register(ClinicalExam)
# # class ClinicalExamAdmin(admin.ModelAdmin):
# #     list_display = ["patient", "doctor", "appointment", "created_at"]
# #     search_fields = ["patient__first_name", "patient__last_name", "doctor__user__first_name", "doctor__user__last_name"]
# #     inlines = [PrescribedMedicationInline]
@admin.register(PatientPrescriptionReport)
class PatientPrescriptionReportAdmin(admin.ModelAdmin):
    # عرض اسم المريض، عدد الأدوية المصروفة، آخر تاريخ صرف، وقائمة الأدوية
    list_display = ["patient_name", "total_prescriptions", "last_prescribed_at", "medications_summary"]
    search_fields = ["first_name", "last_name", "email", "phone", "address"]
    list_per_page = 20

    def get_queryset(self, request):
        """
        نحسّن الاستعلام بضم إحصاءات: العدد وآخر تاريخ،
        ونقلل الاستعلامات لاحقًا.
        """
        qs = super().get_queryset(request)
        # ضم aggregate على جدول PrescribedMedication عبر clinical_exam__patient
        return qs.annotate(
            _total=Count("clinical_exams__prescribed_medications", distinct=False),
            _last=Max("clinical_exams__prescribed_medications__prescribed_at"),
        )

    def patient_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip() or "—"
    patient_name.short_description = "المريض"

    def total_prescriptions(self, obj):
        # قِيمة من الـ annotate
        return getattr(obj, "_total", 0)
    total_prescriptions.short_description = "عدد الأدوية المصروفة"

    def last_prescribed_at(self, obj):
        val = getattr(obj, "_last", None)
        return val or "—"
    last_prescribed_at.short_description = "آخر صرف"

    def medications_summary(self, obj):
        items = (
            PrescribedMedication.objects
            .filter(clinical_exam__patient=obj)
            .select_related("medication")
            .order_by("-prescribed_at")
        )
        if not items.exists():
            return "لا توجد أدوية مصروفة"

        grouped = {}
        for pm in items:
            name = getattr(getattr(pm, "medication", None), "name", None) or "—"
            entry = grouped.setdefault(name, {"count": 0, "lines": []})
            entry["count"] += 1
            entry["lines"].append(
                f"{getattr(pm, 'times_per_day', '—')}×/اليوم، "
                f"{getattr(pm, 'number_of_days', '—')} يوم، "
                f"{getattr(pm, 'dose_unit', '—')}"
            )

        rows = []
        for name, data in grouped.items():
            preview = " | ".join(data["lines"][:2])
            more = f" …(+{len(data['lines'])-2})" if len(data["lines"]) > 2 else ""
            rows.append(
                format_html(
                    "💊 <b>{}</b> <small>(x{})</small><br><span>{}{}</span>",
                    name, data["count"], preview, more
                )
            )
        return format_html_join("\n", "<div style='margin-bottom:6px;'>• {}</div>", ((row,) for row in rows))

    medications_summary.short_description = "ملخص الأدوية"

    # (اختياري) لو تريد “عرض تفصيلي” بدل التجميع:
    # استبدل محتوى medications_summary بما يلي:
    #
    # def medications_summary(self, obj):
    #     items = (
    #         PrescribedMedication.objects
    #         .filter(clinical_exam__patient=obj)
    #         .select_related("medication", "clinical_exam__appointment", "prescribed_by__user")
    #         .order_by("-prescribed_at")
    #     )
    #     if not items.exists():
    #         return "لا توجد أدوية مصروفة"
    #     rows = []
    #     for pm in items:
    #         med_name = getattr(getattr(pm, "medication", None), "name", None) or "—"
    #         appt = getattr(getattr(pm, "clinical_exam", None), "appointment", None)
    #         appt_txt = f"{getattr(appt, 'date', '—')} {getattr(appt, 'time', '')}".strip()
    #         row = (
    #             f"💊 <b>{med_name}</b> — "
    #             f"{getattr(pm, 'times_per_day', '—')}×/اليوم, {getattr(pm, 'number_of_days', '—')} يوم, "
    #             f"{getattr(pm, 'dose_unit', '—')} — "
    #             f"🕒 {getattr(pm, 'prescribed_at', '—')} — "
    #             f"📅 {appt_txt}"
    #         )
    #         rows.append((row,))
    #     return format_html_join("\n", "<div>• {}</div>", rows)