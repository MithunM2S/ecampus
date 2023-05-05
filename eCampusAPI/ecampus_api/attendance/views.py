from rest_framework import viewsets
from attendance import serializers
from .models import AttendanceTracker
from rest_framework.response import Response
from rest_framework import viewsets, mixins, response, status
from django_filters.rest_framework import DjangoFilterBackend
import re




class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AttendanceSerializer
    queryset = AttendanceTracker.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {'class_group':['exact'],
                        'class_name':['exact'],
                        'section':['exact'],
                        'session':['exact'],
                        'attendance_date':['gte', 'lte', 'exact']}


    def perform_create(self, serializer):
        presence_data = serializer.validated_data.get('presence')
        absence_data = serializer.validated_data.get('absence')
        presence_data = ','.join(map(str,presence_data))
        absence_data = ','.join(map(str,absence_data))
        serializer.save(absence=absence_data,presence=presence_data)
        
    def perform_update(self, serializer):
        presence_data = serializer.validated_data.get('presence')
        absence_data = serializer.validated_data.get('absence')
        presence_data = ','.join(map(str,presence_data))
        absence_data = ','.join(map(str,absence_data))
        serializer.save(absence=absence_data,presence=presence_data)

    
    def get_serializer(self, *args, **kwargs):
      if "data" in kwargs:
        self.request_data = kwargs["data"]
        # check if many is required
        if isinstance(self.request_data, list):
            kwargs["many"] = True
      #print(kwargs)

      return super(AttendanceViewSet, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.AttendanceCreateSerializer
        if self.action == 'update':
            return serializers.AttendanceUpdateSerializer
        if self.action == 'list':
            return serializers.AttendanceListSerializer
        return super(AttendanceViewSet, self).get_serializer_class()
    
    '''def create(self, request, *args, **kwargs):
        print("entered in create method")
        serializer = self.get_serializer(data=request.data)
        status=serializer.is_valid(raise_exception=True)
        print('status',serializer)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()'''

    '''def get_queryset(self):
        queryset = AttendanceTracker.objects.all()
        return queryset'''
