"""ecampus_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os
from base.views import ImportStudents
from .serves import * 
from django.conf import settings
from django.contrib import admin

admin.site.site_header = 'Creaxio Administrator'

#APIs
urlpatterns = [
    path('accounts/', admin.site.urls),
    path('attendance/', include('attendance.urls')),
    path('authentication/', include('api_authentication.urls')),
    path('modules/', include('modules.urls')),
    path('master/', include('master.urls')),
    path('employee/', include('employee.urls')),
    path('pre-admission/', include('preadmission.urls')),
    path('student/', include('student.urls')),
    path('fee/', include('fee.urls')),
    path('sms/', include('sendsms.urls')),
]

#Media URLs
urlpatterns += [
    path('media/uploads/documents/<docid>/<path>', protected_document_serve, {'document_root': settings.MEDIA_ROOT}),
    path('media/uploads/student-profile/<studentId>/<path>', protected_student_picture_serve, {'document_root': settings.MEDIA_ROOT}),
    path('media/uploads/institution-profile/<profileId>/<path>', protected_institution_logo_serve, {'document_root': settings.MEDIA_ROOT}),
    path('media/files/fee/<path>', fee_report_file_serve, {'document_root': settings.MEDIA_ROOT}),
]

#Including swagger pags:
if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="eCampus API",
            default_version='v1',
            description="eCampus API services",
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
    urlpatterns += [
        path('', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
        path('api-documents/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('import-student/', ImportStudents.as_view(), name='import_student'),
    ]