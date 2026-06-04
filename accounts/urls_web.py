from django.urls import path
from . import views_web
app_name = 'accounts_web'
urlpatterns = [
    path('doctors/', views_web.DoctorListView.as_view(), name='doctor-list'),
    path('doctors/<uuid:pk>/', views_web.DoctorDetailView.as_view(), name='doctor-detail'),
    path('doctors/create/', views_web.DoctorCreateView.as_view(), name='doctor-create'),
    path('doctors/<uuid:pk>/update/', views_web.DoctorUpdateView.as_view(), name='doctor-update'),
    path('doctors/<uuid:pk>/delete/', views_web.DoctorDeleteView.as_view(), name='doctor-delete'),
    path('login/', views_web.CustomLoginView.as_view(), name='login'),
    path('logout/', views_web.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views_web.ProfileView.as_view(), name='profile'),
]
