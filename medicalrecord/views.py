from rest_framework import generics, views, status
from rest_framework.response import Response

from .models import (
    MedicalRecord,
    Attachment,
    Medication,
    PrescribedMedication,
    MedicationPackage,
    AppliedMedicationPackage,
)

from .serializers import (
    MedicalRecordSerializer,
    MedicalRecordDetailSerializer,
    AttachmentSerializer,
    MedicationSerializer,
    PrescribedMedicationSerializer,
    MedicationPackageSerializer,
    ApplyMedicationPackageSerializer,
    PrescriptionUpsertSerializer,
)

# ================================================
#                السجل الطبي
# ================================================
class MedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    queryset = (MedicalRecord.objects
                .select_related('patient')
                .prefetch_related('attachments'))
    serializer_class = MedicalRecordSerializer


class MedicalRecordRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (MedicalRecord.objects
                .select_related('patient')
                .prefetch_related('attachments'))
    serializer_class = MedicalRecordSerializer


#  عرض سجل طبي كامل حسب المريض
class MedicalRecordByPatientAPIView(views.APIView):
    def get(self, request, patient_id):
        try:
            record = (MedicalRecord.objects
                        .prefetch_related('attachments')
                        .select_related('patient')
                        .get(patient__id=patient_id))
        except MedicalRecord.DoesNotExist:
            return Response({"خطأ": "السجل الطبي غير موجود."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = MedicalRecordDetailSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ================================================
#                    المرفقات
# ================================================
class AttachmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class AttachmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


# ================================================
#                     الأدوية
# ================================================
class MedicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medication.objects.filter(is_active=True)
    serializer_class = MedicationSerializer


class MedicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer


# ================================================
#        الأدوية المصروفة (PrescribedMedication)
# ================================================
class PrescribedMedicationListCreateAPIView(generics.ListCreateAPIView):
    """
    يدعم فلترة عناصر الوصفة حسب الفحص السريري: ?clinical_exam=<id>
    """
    serializer_class = PrescribedMedicationSerializer

    def get_queryset(self):
        qs = (PrescribedMedication.objects
                .select_related('clinical_exam', 'medication', 'prescribed_by'))
        exam_id = self.request.query_params.get('clinical_exam')
        if exam_id:
            qs = qs.filter(clinical_exam_id=exam_id)
        return qs


class PrescribedMedicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (PrescribedMedication.objects
                .select_related('clinical_exam', 'medication', 'prescribed_by'))
    serializer_class = PrescribedMedicationSerializer


# ================================================
#        حِزم الأدوية (Medication Packages)
# ================================================
class MedicationPackageListCreateAPIView(generics.ListCreateAPIView):
    """
    فلترة مدعومة:
        - ?is_active=true|false
        - ?disease=<id>
    """
    serializer_class = MedicationPackageSerializer

    def get_queryset(self):
        qs = (MedicationPackage.objects
                .select_related('disease')
                .prefetch_related('items__medication'))
        is_active = self.request.query_params.get('is_active')
        disease = self.request.query_params.get('disease')

        if is_active is not None:
            if is_active.lower() in ('true', '1'):
                qs = qs.filter(is_active=True)
            elif is_active.lower() in ('false', '0'):
                qs = qs.filter(is_active=False)

        if disease:
            qs = qs.filter(disease_id=disease)

        return qs


class MedicationPackageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (MedicationPackage.objects
                .select_related('disease')
                .prefetch_related('items__medication'))
    serializer_class = MedicationPackageSerializer


class MedicationPackageApplyAPIView(views.APIView):
    """
    تطبيق حزمة أدوية على فحص سريري.
    المسار المقترح: POST /api/medicalrecord/medication-packages/<int:pk>/apply/
    الجسم:
    {
        "clinical_exam_id": 101,
        "mode": "append" | "replace"
    }
    """
    def post(self, request, pk):
        try:
            package = (MedicationPackage.objects
                        .select_related('disease')
                        .prefetch_related('items__medication')
                        .get(pk=pk, is_active=True))
        except MedicationPackage.DoesNotExist:
            return Response({"detail": "الحزمة غير موجودة أو غير مفعلة."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ApplyMedicationPackageSerializer(
            data=request.data,
            context={"request": request, "package": package}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # (اختياري) أعدّ أيضًا عدّاد التطبيقات
        AppliedMedicationPackage.objects.filter(package=package).count()

        return Response(
            {"detail": "تم تطبيق الحزمة بنجاح.", **result},
            status=status.HTTP_201_CREATED
        )


class PrescribedMedicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = PrescribedMedication.objects.select_related("clinical_exam", "medication", "prescribed_by")
    serializer_class = PrescribedMedicationSerializer

class PrescriptionUpsertAPIView(generics.CreateAPIView):
    serializer_class = PrescriptionUpsertSerializer
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = ser.save()              # <-- هذا هو dict الذي أعدته create()
        return Response(result, status=status.HTTP_201_CREATED)