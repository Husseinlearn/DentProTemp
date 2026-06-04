from django.urls import path
from . import views_web
app_name = 'procedures_web'
urlpatterns = [
    path('', views_web.ClinicalExamListView.as_view(), name='exam-list'),
    path('<int:pk>/', views_web.ClinicalExamDetailView.as_view(), name='exam-detail'),
    path('create/', views_web.ClinicalExamCreateView.as_view(), name='exam-create'),
    path('<int:pk>/update/', views_web.ClinicalExamUpdateView.as_view(), name='exam-update'),
    path('<int:pk>/delete/', views_web.ClinicalExamDeleteView.as_view(), name='exam-delete'),
]
