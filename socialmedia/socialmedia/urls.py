"""
URL configuration for socialmedia project.

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
from django.urls import path, re_path, include
from django.views.generic import TemplateView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Quản Lý Hồ Sơ Người Dùng",
        default_version='v1',
        description='APIs quản lý thông tin cá nhân cho hệ thống Alumni',
        contact=openapi.Contact(email='baominh14022004@gmail.com'),
        license=openapi.License(name='NguyenQuangBaoMinh')
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [

    path('',include('socialmediabook.urls')),
    path('admin/', admin.site.urls),

    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),


    path('',TemplateView.as_view(template_name='index.html')),
    re_path(r'^ckeditor/',
    include('ckeditor_uploader.urls')),

    #swagger UI
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
