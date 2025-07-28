"""
URL configuration for Iris_Project project.

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
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('custom_admin/', views.custom_admin, name='custom_admin'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    path('predict/',views.predict, name='predict'),
    path('register/',views.register_view, name='register'),
    path('',views.register_view, name='register'),  
    path('login/',views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path("predict/result",views.result, name='result'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
