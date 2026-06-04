from django.urls import path
from . import views_web

app_name = 'appointments_web'

urlpatterns = [
    path('', views_web.AppointmentListView.as_view(), name='appointment-list'),
    path('<int:pk>/', views_web.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('create/', views_web.AppointmentCreateView.as_view(), name='appointment-create'),
    path('<int:pk>/update/', views_web.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('<int:pk>/delete/', views_web.AppointmentDeleteView.as_view(), name='appointment-delete'),
]
