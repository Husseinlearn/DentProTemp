from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from .models import (
    ClinicalExam,
    ClinicalExamItem,
    ProcedureCategory,
    DentalProcedure,
    Toothcode,
)
from accounts.models import Doctor
from appointment.models import Appointment
from rest_framework.response import Response
from rest_framework.views import APIView


# =====================================================================
# مرن: يقبل id أو الاسم (أو أي حقل slug تختاره) ويرجعه ككائن
# =====================================================================
class FlexiblePKOrSlugRelatedField(serializers.Field):
    """
    يسمح بإدخال الكيانات عبر الـ id أو عبر اسم (slug_field).
    مفيد لحقول مثل: الإجراء بالاسم، السن برقم السن...إلخ
    """
    def __init__(self, queryset, slug_field='name', prefer_slug=False, **kwargs):
        super().__init__(**kwargs)
        self.queryset = queryset
        self.slug_field = slug_field
        self.prefer_slug = prefer_slug

    def to_representation(self, value):
        return value.pk if value is not None else None

    def _get_by_pk(self, pk):
        return self.queryset.get(pk=pk)

    def _get_by_slug(self, slug):
        lookup = {f"{self.slug_field}__iexact": str(slug).strip()}
        return self.queryset.get(**lookup)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            if 'id' in data and data['id'] not in (None, ''):
                try:
                    return self._get_by_pk(int(data['id']))
                except (ValueError, ObjectDoesNotExist):
                    raise serializers.ValidationError(f"Object with id={data['id']} not found.")
            if self.slug_field in data and data[self.slug_field]:
                try:
                    return self._get_by_slug(data[self.slug_field])
                except MultipleObjectsReturned:
                    raise serializers.ValidationError(
                        f"Multiple objects found for {self.slug_field}='{data[self.slug_field]}'. Please use id."
                    )
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        f"Object with {self.slug_field}='{data[self.slug_field]}' not found."
                    )
            raise serializers.ValidationError(f"Provide either 'id' or '{self.slug_field}'.")

        if isinstance(data, int) or (isinstance(data, str) and data.strip() != ''):
            s = str(data).strip()
            is_digit = s.isdigit()

            if is_digit and self.prefer_slug:
                try:
                    return self._get_by_slug(s)
                except MultipleObjectsReturned:
                    raise serializers.ValidationError(
                        f"Multiple objects found for {self.slug_field}='{s}'. Please use id."
                    )
                except ObjectDoesNotExist:
                    try:
                        return self._get_by_pk(int(s))
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError(f"Object with id={s} not found.")

            if is_digit:
                try:
                    return self._get_by_pk(int(s))
                except ObjectDoesNotExist:
                    try:
                        return self._get_by_slug(s)
                    except MultipleObjectsReturned:
                        raise serializers.ValidationError(
                            f"Multiple objects found for {self.slug_field}='{s}'. Please use id."
                        )
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError(
                            f"Object not found by id or {self.slug_field}='{s}'."
                        )

            try:
                return self._get_by_slug(s)
            except MultipleObjectsReturned:
                raise serializers.ValidationError(
                    f"Multiple objects found for {self.slug_field}='{s}'. Please use id."
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Object with {self.slug_field}='{s}' not found.")

        raise serializers.ValidationError("Invalid value type.")


# =====================================================================
# Basic / dictionary serializers
# =====================================================================
class ProcedureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureCategory
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        qs = ProcedureCategory.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("هذا التصنيف موجود بالفعل.")
        return value.strip()


class DentalProcedureSerializer(serializers.ModelSerializer):
    category = FlexiblePKOrSlugRelatedField(
        queryset=ProcedureCategory.objects.all(),
        slug_field='name',
        prefer_slug=False
    )
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = DentalProcedure
        fields = ["id", "name", "description", "default_price", "is_active", "category", "category_name"]
        read_only_fields = ["id"]


class ToothcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toothcode
        fields = ["id", "tooth_number", "tooth_type", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


# =====================================================================
# Clinical Exam + Items
# =====================================================================
class ClinicalExamItemSerializer(serializers.ModelSerializer):
    procedure_name = serializers.CharField(source="procedure.name", read_only=True)
    category_name = serializers.CharField(source="procedure.category.name", read_only=True)
    tooth_number = serializers.CharField(source="toothcode.tooth_number", read_only=True)
    tooth_type = serializers.CharField(source="toothcode.tooth_type", read_only=True)

    class Meta:
        model = ClinicalExamItem
        fields = [
            "id",
            "clinical_exam",
            "procedure",
            "procedure_name",
            "category_name",
            "toothcode",
            "tooth_number",
            "tooth_type",
            "notes",
            "performed_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "procedure_name", "category_name", "tooth_number", "tooth_type"]


class ClinicalExamSerializer(serializers.ModelSerializer):
    patient_display = serializers.SerializerMethodField()
    doctor_display = serializers.SerializerMethodField()
    items = ClinicalExamItemSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalExam
        fields = [
            "id", "patient", "doctor", "appointment",
            "complaint", "medical_advice",
            "created_at",
            "patient_display", "doctor_display",
            "items",
        ]
        read_only_fields = ["id", "created_at", "patient_display", "doctor_display", "items"]

    def get_patient_display(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}" if obj.patient_id else None

    def get_doctor_display(self, obj):
        try:
            return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}" if obj.doctor_id else None
        except Exception:
            return None


# =====================================================================
# Submit-all-in-one Serializer (يعتمد على appointment)
# =====================================================================
class ClinicalExamSubmitSerializer(serializers.Serializer):
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all())

    # حقول الفحص
    complaint = serializers.CharField(allow_blank=True, required=False)
    medical_advice = serializers.CharField(allow_blank=True, required=False)

    # إجراءات متعددة + أسنان متعددة
    procedures = serializers.PrimaryKeyRelatedField(
        queryset=DentalProcedure.objects.filter(is_active=True), many=True
    )
    teeth = serializers.PrimaryKeyRelatedField(queryset=Toothcode.objects.all(), many=True, required=False)
    tooth_numbers = serializers.ListField(child=serializers.CharField(), required=False)

    # خيارات إضافية
    notes = serializers.CharField(allow_blank=True, required=False)
    performed_by = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False, allow_null=True)
    replace_items = serializers.BooleanField(required=False, default=True)

    def validate(self, data):
        if not data.get("procedures"):
            raise serializers.ValidationError({"procedures": "اختر إجراءً واحدًا على الأقل."})

        if not data.get("teeth") and not data.get("tooth_numbers"):
            raise serializers.ValidationError("أرسل teeth (IDs) أو tooth_numbers (أرقام الأسنان).")

        # تحويل أرقام الأسنان إلى كائنات Toothcode
        if data.get("tooth_numbers"):
            nums = [str(n).strip() for n in data["tooth_numbers"] if str(n).strip()]
            found = list(Toothcode.objects.filter(tooth_number__in=nums))
            found_nums = {t.tooth_number for t in found}
            missing = [n for n in nums if n not in found_nums]
            if missing:
                raise serializers.ValidationError({"tooth_numbers": f"أرقام أسنان غير موجودة: {missing}"})
            data["teeth"] = found
        return data

    def create(self, validated_data):
        appt = validated_data["appointment"]
        complaint = validated_data.get("complaint", "")
        advice = validated_data.get("medical_advice", "")
        procs = validated_data["procedures"]
        teeth = validated_data["teeth"]
        notes = validated_data.get("notes", "")
        replace = validated_data.get("replace_items", True)

        performed_by = validated_data.get("performed_by")
        if not performed_by and getattr(appt, "doctor_id", None):
            performed_by = appt.doctor

        with transaction.atomic():
            # (1) إنشاء/تحديث الفحص على أساس appointment
            exam, created = ClinicalExam.objects.get_or_create(
                appointment=appt,
                defaults={
                    "patient": getattr(appt, "patient", None),
                    "doctor": getattr(appt, "doctor", None),
                    "complaint": complaint,
                    "medical_advice": advice,
                }
            )
            if not created:
                exam.complaint = complaint
                exam.medical_advice = advice
                exam.save(update_fields=["complaint", "medical_advice"])

            # (2) استبدال العناصر القديمة إن لزم
            if replace:
                ClinicalExamItem.objects.filter(clinical_exam=exam).delete()

            # (3) إنشاء العناصر (إجراء × سن)
            rows = [
                ClinicalExamItem(
                    clinical_exam=exam,
                    procedure=p,
                    toothcode=t,
                    notes=notes,
                    performed_by=performed_by,
                )
                for p in procs for t in teeth
            ]
            ClinicalExamItem.objects.bulk_create(rows, ignore_conflicts=True)

        # مهم: أعِد جلب exam مع العناصر الجديدة
        exam = (
            ClinicalExam.objects
            .select_related("patient", "doctor", "appointment", "doctor__user")
            .prefetch_related(
                "items",
                "items__procedure",
                "items__procedure__category",
                "items__toothcode"
            )
            .get(pk=exam.pk)
        )
        # نُعيد exam فقط (بدون items خارجية)
        return exam

    def to_representation(self, instance):
        # instance هنا هو ClinicalExam
        return {
            "exam": ClinicalExamSerializer(instance).data
        }


# =====================================================================
# Nested display for categories with procedures (للواجهات)
# =====================================================================
class DentalProcedureInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalProcedure
        fields = ["id", "name", "description", "default_price", "is_active"]


class ProcedureCategoryDetailSerializer(serializers.ModelSerializer):
    procedures = DentalProcedureInlineSerializer(many=True, read_only=True)

    class Meta:
        model = ProcedureCategory
        fields = ["id", "name", "description", "created_at", "procedures"]
        read_only_fields = ["id", "created_at", "procedures"]
