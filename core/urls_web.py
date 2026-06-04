from django.urls import path
from . import views_web

app_name = 'core_web'

urlpatterns = [
    path('', views_web.DashboardView.as_view(), name='dashboard'),
]
