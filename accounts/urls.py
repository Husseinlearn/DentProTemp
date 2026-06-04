from django.urls import path
from . import views


urlpatterns = [
    path('register-user/', views.register_user, name='register-user'),
    path('update-user/', views.update_user, name='update-user'),
    path('login-user/', views.login_user, name='login_user'),
    path('current-user/', views.current_user, name='current_user'),
    path('list-users/', views.list_users, name='list_users'),
    path('doctor-list/', views.DoctorListSimpleAPIView.as_view(), name='doctor_list'),
    path('doctors/<uuid:id>/', views.DoctorDetailAPIView.as_view(), name='doctor-detail'),
    # path('logout_user/', views.logout_user, name='logout_user'),
]