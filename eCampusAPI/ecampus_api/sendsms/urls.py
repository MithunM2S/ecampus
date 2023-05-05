# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:10:45 2021

@author: Prem
"""
from django.urls import path, include
from sendsms.views import *
from rest_framework import routers

router = routers.SimpleRouter()
# router.register(r'template', TemplateViewSet)
router.register(r'group', GroupViewSet)

urlpatterns = [
    path('templates/', TemplateViewSet.as_view(), name='templates'),
    path('send-sms/', SendSMSViewSet.as_view({'post':'create'}), name='send_sms'),
    path('send-group-sms/', SendGroupSMSViewSet.as_view({'post':'create'}), name='send_group_sms'),
    path('reports', SmsReportViewSet.as_view({'get':'list'}), name='report'),
    path('detail-report/<pk>', SmsDetailReportViewSet.as_view({'get':'retrieve'}), name='detail_report'),
]

urlpatterns += router.urls
