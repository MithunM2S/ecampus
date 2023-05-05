from django.urls import path, include
from student.views import *
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'attendance', AttendanceViewSet)

urlpatterns = [
    path('new/admission/', ProfileViewSet.as_view({'post':'create'}), name='new_admission'),
    path('profile/<pk>', ProfileViewSet.as_view({'get':'retrieve'}), name='get_profile'),
    path('profile/edit/<pk>', ProfileViewSet.as_view({'put':'update'}), name='update_profile'),
    path('list/', ProfileViewSet.as_view({'get':'list'}), name='list'),
    path('update-profile-picture/<pk>/', UpdateProfilePicture.as_view({'put':'update'}), name='update_profile_pic'),
    path('dashboard-service/', DashboardService.as_view(), name='dashboard_service'),
    path('search/', SearchStudent.as_view(), name='search_student'),
    path('set-status/<pk>', StudentStatus.as_view({'put': 'update'}), name='set_student_state'),
]

#Appending routes
urlpatterns += router.urls