from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ModuleSerializer
from .models import Module
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser
from api_authentication.permissions import HasOrganizationAPIKey, IsSuperUser
from rest_framework import generics

class DashboardModules(generics.ListAPIView):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()


class MasterModules(generics.ListAPIView):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
