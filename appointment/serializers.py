from rest_framework import serializers
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.db.models import Q
from datetime import date ,datetime,time 
from .models import Appointment
from patients.models import Patient
from accounts.models import Doctor

class FlexibleTimeField(serializers.TimeField):
    def to_internal_value(self, value):
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            s = value.strip().lower()

            # دعم العربية: ص/م و "صباحًا/مساءً"
            s = (s.replace("ص", "am")
                    .replace("صباحًا", "am")
                    .replace("صباحا", "am")
                    .replace("م", "pm")
                    .replace("مساءً", "pm")
                    .replace("مساء", "pm"))

            # إزالة المسافات الزائدة بين الرقم و am/pm (مثال: "2pm" أو "2 pm")
            s = " ".join(s.split())

            # لو جاء "2 pm" بدون دقائق، نفترض ":00"
            if any(s.endswith(x) for x in ("am", "pm")) and ":" not in s:
                s = s.replace(" am", ":00 am").replace(" pm", ":00 pm")

            formats = [
                "%H:%M",
                "%H:%M:%S",
                "%I:%M %p",
                "%I %p",
                "%I:%M%p",
                "%I%p",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(s, fmt).time()
                except ValueError:
                    continue

        raise serializers.ValidationError(
            "صيغة الوقت غير صحيحة. الصيغ المقبولة: "
            "HH:MM أو HH:MM:SS (24h) أو hh:mm AM/PM أو h AM/PM "
            "وأيضًا ص/م أو صباحًا/مساءً."
        )

    # لعرض الوقت دائمًا 12 ساعة في الاستجابة
    def to_representation(self, value):
        return value.strftime("%I:%M %p")  # مثال: 02:30 PM

class AppointmentSerializer(serializers.ModelSerializer):
    time = FlexibleTimeField()
    patient_name = serializers.CharField(write_only=True, required=False)
    doctor_name = serializers.CharField(write_only=True, required=False)

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), required=False)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False)

    patient_display = serializers.SerializerMethodField()
    doctor_display = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_display',
            'doctor', 'doctor_name', 'doctor_display',
            'date', 'time', 'status', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'patient_display', 'doctor_display']

    def get_patient_display(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_doctor_display(self, obj):
        return obj.doctor.user.get_full_name()

    def validate(self, data):
        errors = {}

        # ========== التحقق من الطبيب ==========
        doctor = data.get('doctor')
        doctor_name = self.initial_data.get('doctor_name')
        if not doctor and doctor_name:
            try:
                doctor = Doctor.objects.annotate(
                    full_name=Concat('user__first_name', V(' '), 'user__last_name')
                ).get(full_name__iexact=doctor_name.strip())
                data['doctor'] = doctor
            except Doctor.DoesNotExist:
                errors['doctor_name'] = "اسم الطبيب غير موجود."

        if not doctor:
            errors['doctor'] = "يجب تحديد الطبيب إما عبر ID أو الاسم."

        # ========== التحقق من المريض ==========
        patient = data.get('patient')
        patient_name = self.initial_data.get('patient_name')
        if not patient and patient_name:
            try:
                first, last = patient_name.strip().split(" ", 1)
                patient = Patient.objects.get(
                    first_name__iexact=first.strip(),
                    last_name__iexact=last.strip()
                )
                data['patient'] = patient
            except Patient.DoesNotExist:
                errors['patient_name'] = "اسم المريض غير موجود."

        if not patient:
            errors['patient'] = "يجب تحديد المريض إما عبر ID أو الاسم."

        # باقي التحقق فقط إذا لم توجد أخطاء أولاً
        if not errors:
            date_ = data.get('date', getattr(self.instance, 'date', None))
            time_ = data.get('time', getattr(self.instance, 'time', None))

            if date_ and date_ < date.today():
                errors['date'] = "لا يمكن اختيار تاريخ سابق لحجز الموعد."

            if doctor and date_ and time_:
                if Appointment.objects.filter(
                    doctor=doctor,
                    date=date_,
                    time=time_
                ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
                    errors['time'] = "الطبيب لديه موعد آخر في نفس التاريخ والوقت."

            if patient and date_ and time_:
                if Appointment.objects.filter(
                    patient=patient,
                    date=date_,
                    time=time_
                ).exclude(status='ملغي').exclude(id=getattr(self.instance, 'id', None)).exists():
                    errors['time'] = "المريض لديه موعد آخر في نفس التاريخ والوقت."

                active_statuses = ['مؤكد', 'معلق']
                if Appointment.objects.filter(
                    Q(date__gt=date_) | Q(date=date_, time__gt=time_),
                    patient=patient,
                    status__in=active_statuses
                ).exclude(id=getattr(self.instance, 'id', None)).exists():
                    errors['patient'] = "المريض لديه موعد قادم بالفعل ولا يمكن حجز أكثر من موعد."

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        validated_data.pop('patient_name', None)
        validated_data.pop('doctor_name', None)
        return super().create(validated_data)

class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']  # فقط حقل الحالة