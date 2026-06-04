from django.urls import path
from . import views

urlpatterns = [
    # السجل الطبي
    path('medical-records/', views.MedicalRecordListCreateAPIView.as_view(), name='medicalrecord-list-create'),
    path('medical-records/<int:pk>/', views.MedicalRecordRetrieveUpdateDestroyAPIView.as_view(), name='medicalrecord-detail'),

    # عرض السجل الطبي الكامل حسب المريض
    path('patients/<uuid:patient_id>/medical-record/', views.MedicalRecordByPatientAPIView.as_view(), name='medical-record-by-patient'),

    # المرفقات
    path('attachments/', views.AttachmentListCreateAPIView.as_view(), name='attachment-list-create'),
    path('attachments/<int:pk>/', views.AttachmentRetrieveUpdateDestroyAPIView.as_view(), name='attachment-detail'),

    # الأدوية التعريفية
    path('medications/', views.MedicationListCreateAPIView.as_view(), name='medication-list-create'),
    path('medications/<int:pk>/', views.MedicationRetrieveUpdateDestroyAPIView.as_view(), name='medication-detail'),

    # الأدوية المصروفة (CRUD على العناصر الفردية)
    path('prescribed-medications/', views.PrescribedMedicationListCreateAPIView.as_view(), name='prescribed-medication-list-create'),
    path('prescribed-medications/<int:pk>/', views.PrescribedMedicationRetrieveUpdateDestroyAPIView.as_view(), name='prescribed-medication-detail'),

    # الحِزم الدوائية
    path('medication-packages/', views.MedicationPackageListCreateAPIView.as_view(), name='medication-package-list-create'),
    path('medication-packages/<int:pk>/', views.MedicationPackageRetrieveUpdateDestroyAPIView.as_view(), name='medication-package-detail'),
    path('medication-packages/<int:pk>/apply/', views.MedicationPackageApplyAPIView.as_view(), name='medication-package-apply'),

    # إنشاء/تجهيز وصفة كاملة (ملاحظة عامة + عناصر) دفعة واحدة
    path('prescriptions/', views.PrescriptionUpsertAPIView.as_view(), name='prescription-upsert'),
]
