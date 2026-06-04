from django.urls import path
from .views import (
    ClinicalExamListCreateAPIView, ClinicalExamRUDAPIView, ClinicalExamSubmitAPIView,
    ProcedureCategoryListCreateAPIView, ProcedureCategoryRUDAPIView,
    DentalProcedureListCreateAPIView, DentalProcedureRUDAPIView,
    ToothcodeListAPIView,
    ClinicalExamItemListCreateAPIView, ClinicalExamItemRUDAPIView,ProceduresByToothAPIView,ResolveExamByAppointment
)

urlpatterns = [
    # Clinical Exam
    path("clinical-exams/", ClinicalExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("clinical-exams/<int:pk>/", ClinicalExamRUDAPIView.as_view(), name="exam-rud"),
    path("clinical-exams/submit/", ClinicalExamSubmitAPIView.as_view(), name="clinical-exams-submit"),
    path("clinical-exams/resolve/", ResolveExamByAppointment.as_view(), name="exam-resolve"),

    # Dictionaries
    path("categories/", ProcedureCategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", ProcedureCategoryRUDAPIView.as_view(), name="category-rud"),
    path("dental-procedure/", DentalProcedureListCreateAPIView.as_view(), name="definition-list-create"),
    path("dental-procedure/<int:pk>/", DentalProcedureRUDAPIView.as_view(), name="definition-rud"),

    # Teeth
    path("teeth/", ToothcodeListAPIView.as_view(), name="tooth-list"),
    path("exam-items/by-tooth/", ProceduresByToothAPIView.as_view(), name="exam-items-by-tooth"),

    # Exam Items
    path("exam-items/", ClinicalExamItemListCreateAPIView.as_view(), name="exam-item-list-create"),
    path("exam-items/<int:pk>/", ClinicalExamItemRUDAPIView.as_view(), name="exam-item-rud"),
]
