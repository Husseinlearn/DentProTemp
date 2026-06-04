"""
URL configuration for DentPro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse 
from django.views.generic import RedirectView
# from rest_framework_simplejwt.views import TokenObtainPairView
def health(_): return HttpResponse("ok")
urlpatterns = [
    path('', include('core.urls_web')),
    path('health', health),
    path('admin/', admin.site.urls),
    
    # --- DRF API Routes ---
    path('api/accounts/', include('accounts.urls')),  
    path('api/patients/', include('patients.urls')),  
    path('api/appointment/', include('appointment.urls')),  
    path('api/procedures/', include('procedures.urls')),  
    path('api/medical-record/', include('medicalrecord.urls')),  
    path('api/billing/', include('billing.urls')),  
    path('api/core/',include('core.urls')),  
    path('api-auth/', include('rest_framework.urls')),  
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # --- Template Web Routes ---
    path('patients/', include('patients.urls_web')),
    path('appointments/', include('appointment.urls_web')),
    path('procedures/', include('procedures.urls_web')),
    path('medicalrecord/', include('medicalrecord.urls_web')),
    path('billing/', include('billing.urls_web')),
    path('accounts/', include('accounts.urls_web')),
    path('core/', include('core.urls_web')),
]
