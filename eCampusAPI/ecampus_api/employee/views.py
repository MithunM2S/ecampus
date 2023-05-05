import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import response, filters, generics, serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from datetime import date
from django_filters import rest_framework as customfilters
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import ListAPIView, CreateAPIView
from .utils import *
from .serializers import *


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer


class DashboardServiceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        dashboard = DashboardService()

        result = {
            'Dashboard_count': dashboard.get_dep_wise_emp_count()
        }
        return response.Response(result)


class EmployeeProfile(generics.ListAPIView):
    queryset = EmployeeDetails.objects.all()
    serializer_class = EmployeeProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'blood_group',
        'department',
        'designation'
    ]
    search_fields = [
        'blood_group',
        'department',
        'designation'
    ]

    def get(self, request, *args, **kwargs):
        response = super(
            EmployeeProfile,
            self).get(
            request,
            *
            args,
            **kwargs)
        return response


class EmployeeProfilePost(viewsets.ModelViewSet):
    queryset = EmployeeDetails.objects.all()
    serializer_class = EmployeePostSerizlizer


class EmployeeList(generics.ListAPIView):
    queryset = EmployeeDetails.objects.filter(active=True)
    serializer_class = EmployeeListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'class_group',
    ]

    def get(self, request, *args, **kwargs):
        response = super(
            EmployeeList,
            self).get(
            request,
            *
            args,
            **kwargs)
        return response

class EmployeeView(ListAPIView):
    serializer_class = EmployeeProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]


    def get_queryset(self):
        queryset =  EmployeeDetails.objects.filter(id=self.kwargs['pk'])
        return queryset


    def get(self, request, *args, **kwargs):
        response = super(EmployeeView, self).get(request, *args, **kwargs)
        return response


class EmployeeAttendanceCreate(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeAttendaceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        presence=''.join([str(elem,) for elem in request.data['presence']])
        absence=''.join([str(elem,) for elem in request.data['absence']])
        emp_attendance =Attendance()
        emp_attendance.presence = presence
        emp_attendance.absence = absence
        emp_attendance.attendance_date = request.data['attendance_date']
        emp_attendance.department_id = request.data['department']
        emp_attendance.save()
        result = {
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Data Saved Successfully",
        }
        return JsonResponse(result)


# class EmployeeAttendanceList(ListAPIView):
#     serializer_class = EmployeeAttendaceSerializerGet
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = [
#         'attendance_status',
#         'employee_class_group',
#     ]

#     def get_queryset(self):
#         date = self.kwargs['date']
#         queryset =  EmployeeAttendance.objects.filter(attendance_date=date, employee_details__active=True)
#         return queryset


#     def get(self, request, *args, **kwargs):
#         response = super(EmployeeAttendanceList, self).get(request, *args, **kwargs)
#         return response

        

class EmployeeAttendanceUpdate(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeAttendaceSerializer

    def put(self, request,pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        presence=''.join([str(elem,) for elem in request.data['presence']])
        absence=''.join([str(elem,) for elem in request.data['absence']])
        Attendance.objects.filter(id=pk).update(presence=presence,absence=absence)
        result = {
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Data updated Successfully",
        }
        return JsonResponse(result)



class EmployeeInactive(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeInactiveSerializer

    def post(self, request):
        EmployeeDetails.objects.filter(id=request.data['employee_name']).update(active=False)
        print(EmployeeDetails.objects.filter(id=request.data['employee_name']).update(active=False))
        
        result = {
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Employee Deactivated",
        }
        return JsonResponse(result)


class CustomFilter(customfilters.FilterSet):
    class Meta:
        model = Attendance
        fields = ('department', 'attendance_date' )

class AttendanceEmployee(ListAPIView):
    # permission_classes = (IsAuthenticated,)AllowAny 
    queryset = Attendance.objects.all()
    serializer_class = EmpAttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = CustomFilter

    def get_queryset(self):
        date = self.request.query_params['attendance_date']
        queryset =  Attendance.objects.filter(attendance_date=date)
        return queryset


    def get(self, request, *args, **kwargs):
        json_data = {}
        json_data_list = []
        data = self.get_queryset()
        for each in data:
            presence = each.presence.replace(',', '')
            absense = each.absence.replace(',', '')
            for i in presence:
                emp_data = EmployeeDetails.objects.get(id=i)
                json_data['emp_id'] = emp_data.id
                json_data['first_name'] = emp_data.employee_name
                json_data['id'] = each.id
                json_data['status'] = "p"
                json_data_list.append(json_data)
                json_data ={}
            for j in absense:
                emp_data = EmployeeDetails.objects.get(id=j)
                json_data['emp_id'] = emp_data.id
                json_data['first_name'] = emp_data.employee_name
                json_data['id'] = each.id
                json_data['status'] = "ab"
                json_data_list.append(json_data)
                json_data ={}
        if json_data_list:
            final_output = {"code":status.HTTP_200_OK,
            "status":True,
            "message":"OK",
            "data":json_data_list}
        else:
            final_output = {"code":status.HTTP_200_OK,
            "status":True,
            "message":"OK",
            "data":[{}]}

        return JsonResponse(final_output)
    

class EmpModDepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = EmpModDepartmentSerizlizer