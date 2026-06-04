from rest_framework import serializers
from django.db.models.functions import Lower
from .models import (Patient , Disease, Medication, PatientDisease, PatientAllergy) 
from datetime import datetime, date, timedelta
from django.db.models import Q
from django.utils.timezone import localdate, now as tznow
from appointment.models import Appointment
import re

class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        raise serializers.ValidationError("تاريخ الميلاد بتنسيق خاطئ. استخدم YYYY-MM-DD أو DD-MM-YYYY أو DD/MM/YYYY.")
    
class FlexibleItemsField(serializers.ListField):
    """
    هذا يساعدنا عند انشاء المريض يتيح لنا ارسال الامراض المزمنة الادوية الحساسة
    """
    def __init__(self, **kwargs):
        super().__init__(child=serializers.JSONField(), **kwargs)

class AppointmentInlineSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "date", "time", "status", "doctor", "doctor_name"]
# --------------------------------------------------------------------
# Patient Serializer: تسجيل المريض والتحقق من بياناته
# --------------------------------------------------------------------
class PatientSerializer(serializers.ModelSerializer):
    date_of_birth = FlexibleDateField()
    diseases = FlexibleItemsField(write_only=True, required=False)
    allergies = FlexibleItemsField(write_only=True, required=False)
    closest_appointment = serializers.SerializerMethodField(read_only=True)
    chronic_diseases = serializers.SerializerMethodField(read_only=True)
    medication_allergies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'phone',
            'email',
            'address',
            'created_at',
            'updated_at',
            'is_archived',
            'diseases',              # write-only
            'allergies',            # write-only
            'chronic_diseases',     # read-only
            'medication_allergies', 
            'closest_appointment',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    def get_closest_appointment(self, obj):
        """
        يُرجع أقرب موعد قادم للمريض؛ وإن لم يوجد، يُرجع أحدث موعد مضى؛
        وإن لم يوجد أي موعد يُرجع None.
        """
        today = localdate()
        now_time = tznow().time()

        # أقرب موعد قادم (اليوم لاحقًا أو في الأيام القادمة)
        upcoming = (Appointment.objects
                    .filter(patient=obj)
                    .filter(Q(date__gt=today) | Q(date=today, time__gte=now_time))
                    .order_by("date", "time")
                    .first())

        if upcoming:
            return AppointmentInlineSerializer(upcoming).data

        # أحدث موعد مضى (اليوم قبل الآن أو أيام سابقة)
        latest_past = (
            Appointment.objects
            .filter(patient=obj)
            .filter(Q(date__lt=today) | Q(date=today, time__lt=now_time))
            .order_by("-date", "-time")
            .first())

        if latest_past:
            return AppointmentInlineSerializer(latest_past).data

        return None
    # 1- التحقق من الاسم الكامل
    def validate(self, data):
        full_name = f"{data.get('first_name', '').strip()} {data.get('last_name', '').strip()}"
        parts = full_name.split()
        if len(parts) < 4:
            raise serializers.ValidationError("يجب أن يحتوي الاسم الكامل على أربع كلمات على الأقل (الاسم الأول والثاني والثالث والأخير مجتمعين).")
        return data

    # 2- التحقق من تنسيق وتاريخ الميلاد
    def validate_date_of_birth(self, value):
        from datetime import datetime, date

        # إذا كانت القيمة نصية (string) نحللها
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    value = datetime.strptime(value, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise serializers.ValidationError("تاريخ الميلاد بتنسيق خاطئ. استخدم YYYY-MM-DD أو DD-MM-YYYY.")

        # إذا كانت القيمة كائن datetime نحولها إلى date فقط
        elif isinstance(value, datetime):
            value = value.date()

        # تحقق أن التاريخ ليس في المستقبل
        if value > date.today():
            raise serializers.ValidationError("لا يمكن أن يكون تاريخ الميلاد في المستقبل.")

        return value

    # 3- التحقق من الجنس
    def validate_gender(self, value):
        val = value.strip().lower()
        accepted = ['male', 'female', 'other', 'ذكر', 'أنثى', 'انثى', 'غير ذلك', 'اخر', 'آخر']
        if val not in accepted:
            raise serializers.ValidationError(
                "Gender must be one of: ذكر، أنثى، غير ذلك أو male, female, other."
            )
        return value.strip()
    # 4- التحقق من رقم الهاتف
    def validate_phone(self, value):
        if not re.match(r'^7\d{8}$', value):
            raise serializers.ValidationError("رقم الهاتف يجب أن يبدأ بـ 7 ويتكون من 9 أرقام. مثل (7XXXXXXXX).")

        # تحقق من عدم التكرار
        if Patient.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("رقم التلفون موجود مسبقاً.")

        return value
    
    # 5- التحقق من البريد الإلكتروني
    def validate_email(self, value):
        if value and Patient.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("الايميل موجود مسبقاً.")
        return value

    # 6- التحقق من العنوان
    def validate_address(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("العنوان قصير جدا.")
        return value
    # -------------------------
    # أدوات مساعدة للربط/الإنشاء
    # -------------------------
    def _to_int(self, v):
        try:
            return int(v)
        except Exception:
            return None

    def _get_or_create_disease(self, item):
        """
        item يمكن أن يكون:
            - int => id
            - str => name
            - dict فيه 'id' أو 'name'
        """
        if isinstance(item, dict):
            if 'id' in item:
                return Disease.objects.get(pk=item['id'])
            if 'name' in item and str(item['name']).strip():
                name = str(item['name']).strip()
                obj, _ = Disease.objects.get_or_create(
                    name__iexact=name,
                    defaults={'name': name}
                )
                # get_or_create مع lookup case-insensitive: نعمل محاولة يدوية
                if not _:
                    # لو استخدمنا name__iexact لن يسمح defaults، لذا نجرب يدويًا
                    obj = Disease.objects.filter(name__iexact=name).first() or Disease.objects.create(name=name)
                return obj

        if isinstance(item, int):
            return Disease.objects.get(pk=item)

        if isinstance(item, str) and item.strip():
            name = item.strip()
            # محاكاة case-insensitive get_or_create
            existing = Disease.objects.filter(name__iexact=name).first()
            if existing:
                return existing
            return Disease.objects.create(name=name)

        raise serializers.ValidationError("صيغة مرض غير صحيحة. استخدم id أو name أو كائن {id|name}.")

    def _get_or_create_medication(self, item):
        if isinstance(item, dict):
            if 'id' in item:
                return Medication.objects.get(pk=item['id'])
            if 'name' in item and str(item['name']).strip():
                name = str(item['name']).strip()
                existing = Medication.objects.filter(name__iexact=name).first()
                if existing:
                    return existing
                return Medication.objects.create(name=name)

        if isinstance(item, int):
            return Medication.objects.get(pk=item)

        if isinstance(item, str) and item.strip():
            name = item.strip()
            existing = Medication.objects.filter(name__iexact=name).first()
            if existing:
                return existing
            return Medication.objects.create(name=name)

        raise serializers.ValidationError("صيغة دواء/حساسية غير صحيحة. استخدم id أو name أو كائن {id|name}.")

    def _set_patient_diseases(self, patient, diseases_items):
        # احذف الروابط القديمة ثم أضف الجديدة (سلوك استبدال)
        PatientDisease.objects.filter(patient=patient).delete()
        for item in diseases_items:
            disease = self._get_or_create_disease(item if not isinstance(item, str) or not item.isdigit() else int(item))
            PatientDisease.objects.get_or_create(patient=patient, disease=disease)

    def _set_patient_allergies(self, patient, allergies_items):
        PatientAllergy.objects.filter(patient=patient).delete()
        for item in allergies_items:
            medication = self._get_or_create_medication(item if not isinstance(item, str) or not item.isdigit() else int(item))
            PatientAllergy.objects.get_or_create(patient=patient, medication=medication)
    #  دالة الإنشاء
    def create(self, validated_data):
        diseases_items = validated_data.pop('diseases', [])
        allergies_items = validated_data.pop('allergies', [])

        patient = Patient.objects.create(**validated_data)

        if diseases_items:
            self._set_patient_diseases(patient, diseases_items)
        if allergies_items:
            self._set_patient_allergies(patient, allergies_items)

        return patient

    #  دالة التعديل
    def update(self, instance, validated_data):
        diseases_items = validated_data.pop('diseases', None)   # None يعني لم تُرسل
        allergies_items = validated_data.pop('allergies', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if diseases_items is not None:
            self._set_patient_diseases(instance, diseases_items)

        if allergies_items is not None:
            self._set_patient_allergies(instance, allergies_items)

        return instance
    
    
    # -------------------------
    # للعرض فقط
    # -------------------------
    def get_chronic_diseases(self, obj):
        qs = PatientDisease.objects.select_related('disease').filter(patient=obj)
        return [{'id': d.disease.id, 'name': d.disease.name} for d in qs]

    def get_medication_allergies(self, obj):
        qs = PatientAllergy.objects.select_related('medication').filter(patient=obj)
        return [{'id': a.medication.id, 'name': a.medication.name} for a in qs]
# --------------------------------------------------------------------
# Disease Serializer: تسجيل الأمراض والتحقق من أنها غير موجود مسبقًا 
# --------------------------------------------------------------------
class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ["id", "name", "dental_impact", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        qs = Disease.objects.annotate(n=Lower("name")).filter(n=value.strip().lower())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("اسم المرض موجود مسبقًا (بدون حساسية حالة الأحرف).")
        return value.strip()

# --------------------------------------------------------------------
# Medication Serializer: تسجيل الأدوية الحساسة والتحقق من أنها غير موجود مسبقًا 
# --------------------------------------------------------------------
class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["id", "name", "dental_impact", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        qs = Medication.objects.annotate(n=Lower("name")).filter(n=value.strip().lower())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("اسم الدواء موجود مسبقًا (بدون حساسية حالة الأحرف).")
        return value.strip()



    # #  التحقق من الاسم الأول
    # def validate_first_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("First name must contain only letters.")
    #     return value

    # #  التحقق من الاسم الأخير
    # def validate_last_name(self, value):
    #     if not value.strip().isalpha():
    #         raise serializers.ValidationError("Last name must contain only letters.")
    #     return value