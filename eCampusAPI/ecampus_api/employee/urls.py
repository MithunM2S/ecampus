from django.urls import path
from .views import *
from django.urls import re_path



urlpatterns = [

     path('designation/list/',
          DesignationViewSet.as_view({'get': 'list'}),
          name='list_designation'),
     path('designation/create/',
          DesignationViewSet.as_view({'post': 'create'}),
          name='create_designation'),
     path('designation/update/<pk>/',
          DesignationViewSet.as_view({'put': 'update'}),
          name='update_designation'),
     path('designation/delete/<pk>/',
          DesignationViewSet.as_view({'delete': 'destroy'}),
          name='delete_designation'),
     path('dashboard/', DashboardServiceAPI.as_view(), name='dashboard'),
     path(
          'profile/list/',
          EmployeeProfile.as_view(),
          name='emp_profile_list'),
     path('profile/create/',
          EmployeeProfilePost.as_view({'post': 'create'}),
          name='emp_profile_create'),
     path('profile/update/<pk>/',
          EmployeeProfilePost.as_view({'put': 'update'}),
          name='emp_profile_update'),
     path('profile/delete/<pk>/',
          EmployeeProfilePost.as_view({'delete': 'destroy'}),
          name='emp_profile_delete'),
     path('profile/view/<pk>', EmployeeView.as_view()),
     path('employee_list/', EmployeeList.as_view(), name='employee_list'),
     path('employee_attendance/create/', EmployeeAttendanceCreate.as_view()),
     # path('employee_attendance/list/<date>/', EmployeeAttendanceList.as_view()),
     path('employee_attendance/update/<pk>/', EmployeeAttendanceUpdate.as_view()),
     path('deactivate_employee/', EmployeeInactive.as_view()),


     path('employee_attendance/list/', AttendanceEmployee.as_view(), name='create_attendance_emp'),

     path('department/list/', EmpModDepartmentViewSet.as_view({'get':'list'}), name='list_department'),
     path('department/create/', EmpModDepartmentViewSet.as_view({'post':'create'}), name='create_department'),
     path('department/update/<pk>/', EmpModDepartmentViewSet.as_view({'put':'update'}), name='update_department'),
     path('department/delete/<pk>/', EmpModDepartmentViewSet.as_view({'delete':'destroy'}), name='delete_department'),

]
