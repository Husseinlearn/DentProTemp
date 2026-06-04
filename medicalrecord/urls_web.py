from django.urls import path
from . import views_web
app_name = 'medicalrecord_web'
urlpatterns = [
    path('', views_web.MedicalRecordListView.as_view(), name='record-list'),
    path('<int:pk>/', views_web.MedicalRecordDetailView.as_view(), name='record-detail'),
    path('create/', views_web.MedicalRecordCreateView.as_view(), name='record-create'),
    path('<int:pk>/update/', views_web.MedicalRecordUpdateView.as_view(), name='record-update'),
    path('<int:pk>/delete/', views_web.MedicalRecordDeleteView.as_view(), name='record-delete'),
    path('attachments/create/', views_web.AttachmentCreateView.as_view(), name='attachment-create'),
]
