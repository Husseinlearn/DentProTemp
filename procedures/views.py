from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from appointment.models import Appointment
from rest_framework.views import APIView

from .models import (
    ClinicalExam,
    ClinicalExamItem,
    ProcedureCategory,
    DentalProcedure,
    Toothcode,
)
from .serializers import (
    ClinicalExamSerializer,
    ClinicalExamItemSerializer,
    ClinicalExamSubmitSerializer,
    ProcedureCategorySerializer,
    ProcedureCategoryDetailSerializer,
    DentalProcedureSerializer,
    ToothcodeSerializer,
)

# ---------------------------
# ClinicalExam
# ---------------------------
class ClinicalExamListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer
    filterset_fields = ["patient", "doctor", "appointment"]
    search_fields = ["complaint", "medical_advice"]  # لا يوجد planned_procedures الآن
    ordering_fields = ["created_at"]


class ClinicalExamRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClinicalExam.objects.select_related("patient", "doctor", "appointment").all()
    serializer_class = ClinicalExamSerializer


# عند الضغط على "حفظ" من الواجهة: إنشاء/تحديث الفحص + إنشاء عناصر (إجراء × سن) دفعة واحدة
class ClinicalExamSubmitAPIView(generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]   # عدّل حسب نظامك
    serializer_class = ClinicalExamSubmitSerializer


# ---------------------------
# Dictionary: Categories & Procedures
# ---------------------------
class ProcedureCategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProcedureCategorySerializer

    def get_queryset(self):
        qs = ProcedureCategory.objects.all()
        if self.request.method == "GET":
            qs = qs.prefetch_related("procedures")
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProcedureCategoryDetailSerializer
        return ProcedureCategorySerializer


class ProcedureCategoryRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcedureCategorySerializer

    def get_queryset(self):
        qs = ProcedureCategory.objects.all()
        if self.request.method == "GET":
            qs = qs.prefetch_related("procedures")
        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProcedureCategoryDetailSerializer
        return ProcedureCategorySerializer


class DentalProcedureListCreateAPIView(generics.ListCreateAPIView):
    queryset = DentalProcedure.objects.select_related("category").all()
    serializer_class = DentalProcedureSerializer
    filterset_fields = ["is_active", "category"]
    search_fields = ["name", "description"]


class DentalProcedureRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DentalProcedure.objects.select_related("category").all()
    serializer_class = DentalProcedureSerializer


# ---------------------------
# Toothcode
# ---------------------------
class ToothcodeListAPIView(generics.ListAPIView):
    queryset = Toothcode.objects.all()
    serializer_class = ToothcodeSerializer
    filterset_fields = ["tooth_type", "tooth_number"]
    search_fields = ["tooth_number", "description"]
    ordering_fields = ["tooth_type", "tooth_number"]


# ---------------------------
# ClinicalExam Items (إجراء × سن)
# ---------------------------
class ClinicalExamItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClinicalExamItem.objects.select_related(
        "clinical_exam", "procedure", "toothcode", "performed_by"
    ).all()
    serializer_class = ClinicalExamItemSerializer
    filterset_fields = ["clinical_exam", "procedure", "toothcode", "performed_by"]
    ordering_fields = ["created_at"]


class ClinicalExamItemRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClinicalExamItem.objects.select_related(
        "clinical_exam", "procedure", "toothcode", "performed_by"
    ).all()
    serializer_class = ClinicalExamItemSerializer


class ProceduresByToothAPIView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get_tooth(self, request):
        """
        يدعم:
        - ?tooth=31&by=number  -> tooth_number='31'
        - ?tooth=31&by=id      -> pk=31
        - ?tooth=31            -> auto: يجرّب tooth_number أولًا ثم id
        """
        tooth_param = request.query_params.get("tooth")
        if not tooth_param:
            raise Http404("tooth is required")

        mode = (request.query_params.get("by") or "auto").lower().strip()
        s = str(tooth_param).strip()

        if mode == "id":
            if not s.isdigit():
                raise Http404("tooth id must be numeric")
            return get_object_or_404(Toothcode, pk=int(s))

        if mode == "number":
            return get_object_or_404(Toothcode, tooth_number__iexact=s)

        # auto: جرّب رقم السن أولًا، ثم pk إن لم يوجد
        try:
            return Toothcode.objects.get(tooth_number__iexact=s)
        except Toothcode.DoesNotExist:
            pass
        except Toothcode.MultipleObjectsReturned:
            # إذا رقم السن غير فريد، يمكنك إجبار الاستعلام بـ by=number أو جعل tooth_number فريد
            return get_object_or_404(Toothcode, tooth_number__iexact=s)

        if s.isdigit():
            return get_object_or_404(Toothcode, pk=int(s))

        # غير رقمي ولم نجده كرقم سن (لن يصل هنا عادة)
        return get_object_or_404(Toothcode, tooth_number__iexact=s)

    def get(self, request):
        tooth = self.get_tooth(request)
        qs = ClinicalExamItem.objects.select_related(
            "clinical_exam", "procedure", "procedure__category", "toothcode", "performed_by"
        ).filter(toothcode=tooth)

        exam_id = request.query_params.get("exam")
        appt_id = request.query_params.get("appointment")
        patient_id = request.query_params.get("patient")

        if exam_id:
            qs = qs.filter(clinical_exam_id=exam_id)
        elif appt_id:
            qs = qs.filter(clinical_exam__appointment_id=appt_id)
        if patient_id:
            qs = qs.filter(clinical_exam__patient_id=patient_id)

        distinct = request.query_params.get("distinct")
        if distinct in ("1", "true", "True"):
            procs = (qs.values(
                        "procedure", "procedure__name",
                        "procedure__category", "procedure__category__name"
                    )
                    .order_by("procedure")
                    .distinct())
            return Response({
                "tooth": {"id": tooth.id, "number": tooth.tooth_number},
                "count": qs.count(),
                "procedures": list(procs),
            })

        data = ClinicalExamItemSerializer(qs, many=True).data
        return Response({
            "tooth": {"id": tooth.id, "number": tooth.tooth_number},
            "count": len(data),
            "items": data,
        })
    
class ResolveExamByAppointment(APIView):
    def get(self, request):
        appt_id = request.query_params.get("appointment")
        if not appt_id:
            return Response({"detail": "appointment مطلوب"}, status=400)

        appt = Appointment.objects.select_related("patient","doctor").get(pk=appt_id)
        exam, _ = ClinicalExam.objects.get_or_create(
            appointment=appt,
            defaults={"patient": appt.patient, "doctor": appt.doctor}
        )
        return Response({"clinical_exam": exam.id}, status=200)