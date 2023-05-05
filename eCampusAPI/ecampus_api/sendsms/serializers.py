# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:20:08 2021
@author: Prem
"""

from sendsms.models import Template, SMSTracker, Group
from rest_framework import serializers
import ast
from student import models as student_models
from master import services as master_services
from master import models as master_models


# class TemplateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Template
#         fields = "__all__"


# class CreateOrUpdateTemplateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Template
#         exclude = [
#             'created_by',
#             'updated_by'
#         ]


class SendSmsSerializer(serializers.ModelSerializer):
    student_id = serializers.JSONField()
    class_id = serializers.JSONField()
    class_group = serializers.JSONField()
    section = serializers.JSONField()
    addtional_numbers = serializers.JSONField()

    class Meta:
        model = SMSTracker
        fields = [
            'template_id',
            'student_id',
            'class_id',
            'class_group',
            'section',
            'addtional_numbers',
            'message_content',
        ]
    
    def validate(self,validate_data):
        errors = {}
        student_id = validate_data.get('student_id', None)
        class_id = validate_data.get('class_id', None)
        class_group = validate_data.get('class_group', None)
        section = validate_data.get('section', None)
        addtional_numbers = validate_data.get('addtional_numbers', None)
        if not isinstance(student_id, list):
            errors['student_id'] = 'filed should an array'
        if not isinstance(class_id, list):
            errors['class_id'] = 'filed should an array'
        if not isinstance(class_group, list):
            errors['class_group'] = 'filed should an array'
        if not isinstance(addtional_numbers, list):
            errors['addtional_numbers'] = 'filed should an array'
        if errors:
            raise serializers.ValidationError(errors)
        else:
            recipients_list = student_id + class_id + class_group + section + addtional_numbers 
            if not recipients_list:
                raise serializers.ValidationError("Recipients list can not  empty.")
        return validate_data

class GroupSmsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSTracker
        fields = [
            'template_id',
            'group',
            'message_content',
        ]
    
    def validate(self,validate_data):
        errors = {}
        group = validate_data.get('group', None)
        if not group:
            errors['group'] = 'is required'
        if errors:
            raise serializers.ValidationError(errors)
        return validate_data


class SmsReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSTracker
        fields = [
            'id',
            'reference_number',
            'batch_id',
            'group',
            'client_request_status',
            'vendor_reponse_status',
            'vendor_error',
            'created_on',
            'created_by',
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['group'] = master_services.get_related(instance.group, 'name')
        return response


class SmsDetailReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSTracker
        fields = [
            'id',
            'reference_number',
            'batch_id',
            'client_request',
            'vendor_response',
            'addtional_numbers',
            'message_content',
            'created_on',
            'vendor_warning',
            'vendor_error',
            'group',
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        vendor_reposnse = response.get('vendor_response')
        client_request = response.get('client_request')
        addtional_numbers = response.get('addtional_numbers')
        if vendor_reposnse  and client_request:
            vendor_reposnse = ast.literal_eval(vendor_reposnse)
            client_request = ast.literal_eval(client_request)
            successed, failed = self.get_successes_and_failed_recipients(client_request, vendor_reposnse)
            student_queryset = student_models.Profile.objects.values('id', 'first_name')
            successed_student = student_queryset.filter(id__in=successed)
            failed_student = student_queryset.filter(id__in=failed)
            response['successed'] = successed_student
            response['failed'] = failed_student
        if addtional_numbers:
            addtional_numbers = ast.literal_eval(addtional_numbers)
            response['addtional_numbers'] = addtional_numbers
            non_track_successed, non_track_failed = self.get_successes_and_failed_non_track_recipients(addtional_numbers, vendor_reposnse)
            response['sucessed_addtional_numbers'] = non_track_successed
            response['failed_addtional_numbers'] = non_track_failed
        if not vendor_reposnse:
            response['batch_failed'] = 'The entier batch failed due to the vednor no response.'
        response['group'] = master_services.get_related(instance.group, 'name')
        del response['vendor_response']
        del response['client_request']
        return response
    
    def get_successes_and_failed_recipients(self, client_data, vendor_data):
        successed, failed = [], []
        for key, value in client_data.items():
            key = int(key)
            if int('91' + str(value)) in vendor_data.values():
                successed.append(key)
            else:
                failed.append(key)
        return successed, failed

    def get_successes_and_failed_non_track_recipients(self, addtional_numbers, vendor_data):
        addt_successed, addt_failed = [], []
        for number in addtional_numbers:
            if int('91' + str(number)) in vendor_data.values():
                addt_successed.append(number)
            else:
                addt_failed.append(number)
        return addt_successed, addt_failed


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        exclude = ['members', 'updated_by', 'updated_on', 'created_on']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        students = response.get('students')
        class_groups = response.get('class_groups')
        classes = response.get('classes')
        sections = response.get('sections')
        employees = response.get('employees')
        employee_groups = response.get('employee_groups')
        response['students'] = student_models.Profile.objects.values('id', 'first_name', 'student_id').filter(id__in=ast.literal_eval(students))
        response['class_groups'] = master_models.ClassGroup.objects.values('id', 'class_group').filter(id__in=ast.literal_eval(class_groups))
        response['classes'] = master_models.ClassName.objects.values('id', 'class_name').filter(id__in=ast.literal_eval(classes))
        response['sections'] = master_models.Section.objects.values('id', 'section_name').filter(id__in=ast.literal_eval(sections))
        # response['employees'] = ast.literal_eval(employees)
        # response['employee_groups'] = ast.literal_eval(employee_groups)
        return response


class GroupCreateOrUpdateSerializer(serializers.ModelSerializer):
    students = serializers.JSONField()
    classes = serializers.JSONField()
    class_groups = serializers.JSONField()
    sections = serializers.JSONField()
    employees = serializers.JSONField()
    employee_groups = serializers.JSONField()

    class Meta:
        model = Group
        fields = [
            'name',
            'students',
            'classes',
            'class_groups',
            'sections',
            'employees',
            'employee_groups',
        ]

    def validate(self,validate_data):
        errors = {}
        students_list = validate_data.get('students', [])
        classes_list = validate_data.get('classes', [])
        class_groups_list = validate_data.get('class_groups', [])
        sections_list = validate_data.get('sections', [])
        employees_list = validate_data.get('employees', [])
        employee_groups_list = validate_data.get('employee_groups', [])
        if not isinstance(students_list, list):
            errors["students"] = 'filed should an array'
        if not isinstance(classes_list, list):
            errors["classes"] = 'filed should an array' 
        if not isinstance(class_groups_list, list):
            errors["class_groups"] = 'filed should an array'
        if not isinstance(sections_list, list):
            errors["sections"] = 'filed should an array'
        if not isinstance(employees_list, list):
            errors["employees"] = 'filed should an array'
        if not isinstance(employee_groups_list, list):
            errors["employee_groups"] = 'filed should an array'
        if errors:
            raise serializers.ValidationError(errors)
        else:
            members_list = students_list + classes_list + class_groups_list + sections_list + employees_list + employee_groups_list
            if not members_list:
                raise serializers.ValidationError("Group members can not  empty.")
        return validate_data
