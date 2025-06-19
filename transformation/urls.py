"""
URL configuration for transformation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apptransformation.views import RegisterView
from apptransformation.views import ProtectedView
from apptransformation.views import index_page,services_page,contact_page,about_page
from apptransformation import views
from django.urls import path
#from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # User Registration
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # JWT Login & Refresh
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
    
    path('', index_page),
    path('services/', services_page),
    path('about/', about_page),
    path('contact/', contact_page),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
   
   
    path('upload/', views.upload_template, name='upload_template'),
    path('download_file/<str:filename>/', views.download_file, name='download_file'),
    path('download/<str:filename>/', views.download_view, name='download_view'),
    path('services/', views.services, name='services'),
    path('transformation-login/', views.transformation_login, name='transformation_login'),
    path('contact/', views.contact_page, name='contact')


]
