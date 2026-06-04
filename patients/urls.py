from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.routers import DefaultRouter


routers = DefaultRouter()
routers.register(r'diseases', views.DiseaseViewSet, basename='disease')
routers.register(r'medications', views.MedicationViewSet, basename='medication')

urlpatterns = [
    path('', views.PatientListCreateAPIView.as_view(), name='patient-list-create'),
    path('patient/<uuid:pk>/', views.PatientRetrieveUpdateDestroyAPIView.as_view(), name='patient-retrieve-update-destroy'),
    path('patient-detail/<uuid:id>/', views.PatientDetailAPIView.as_view(), name='patient-detail'),
    path('side-effects/', include(routers.urls)),  # Include the router URLs for Disease and Medication
    
]