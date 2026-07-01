from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from .models import Disease, Patient, Medication
from .serializers import DiseaseSerializer, PatientSerializer, MedicationSerializer
from rest_framework import permissions, viewsets
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from .filters import PatientFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from accounts.permissions_utils import IsDoctor, IsReceptionist, IsManager

# Create your views here.
class PatientListCreateAPIView(generics.ListCreateAPIView):
    """عرض وإنشاء المرضى"""
    queryset = Patient.objects.filter(is_archived=False)
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PatientFilter
    #  البحث في هذه الحقول
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'address']

    #  السماح بالترتيب حسب الحقول التالية 
    ordering_fields = ['first_name', 'last_name', 'date_of_birth', 'created_at']
    ordering = ['created_at']  # ترتيب افتراضي
    
    # Example of custom role permissions: Only Receptionist or Manager can view/create patients
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientRetrieveUpdateDestroyAPIView(APIView):
    """عرض وتعديل وحذف (أرشفة) مريض"""
    permission_classes = [IsAuthenticated]  

    def get_object(self, pk):
        return get_object_or_404(Patient, pk=pk, is_archived=False)
    
    def get(self, request, pk):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_object(pk)
        patient.delete()  # This will soft delete (set is_archived to True)
        return Response({'رسالة': 'تم حذف المريض بنجاح'}, status=status.HTTP_204_NO_CONTENT)

class PatientDetailAPIView(generics.RetrieveAPIView):
    queryset = Patient.objects.filter(is_archived=False)
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

# --------------------------------------------------------------------
# Disease ViewSet:إنشاء وعرض وتعديل وحذف الأمراض
# --------------------------------------------------------------------
class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.all().order_by("name")
    serializer_class = DiseaseSerializer
    permission_classes = [IsAuthenticated]  # Enforce authenticated access

# --------------------------------------------------------------------
# Medication ViewSet:إنشاء وعرض وتعديل وحذف الأدوية
# --------------------------------------------------------------------
class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by("name")
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]  # Enforce authenticated access