from django.urls import path, include
from .views import AttendanceViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('create/', AttendanceViewSet.as_view({'post':'create'}), name='create_attendance'),
    path('update/<pk>/', AttendanceViewSet.as_view({'put':'update'}), name='update_attendance'),
    path('report/', AttendanceViewSet.as_view({'get': 'list'}), name='Report'),
    path('list/', AttendanceViewSet.as_view({'get': 'list'}), name='List API'),

]
