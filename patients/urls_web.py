from django.urls import path
from . import views_web

app_name = 'patients_web'

urlpatterns = [
    path('', views_web.PatientListView.as_view(), name='patient-list'),
    path('patient/<uuid:pk>/', views_web.PatientDetailView.as_view(), name='patient-detail'),
    path('patient/create/', views_web.PatientCreateView.as_view(), name='patient-create'),
    path('patient/<uuid:pk>/update/', views_web.PatientUpdateView.as_view(), name='patient-update'),
    path('patient/<uuid:pk>/delete/', views_web.PatientDeleteView.as_view(), name='patient-delete'),
]
