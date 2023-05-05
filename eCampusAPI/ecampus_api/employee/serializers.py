from django.contrib.auth.models import Group as Role, Permission
from django.db.models import fields
from django.db.models.base import Model
from django.db.models.query_utils import FilteredRelation
from rest_framework import serializers
from .models import *
from django.conf import settings
from api_authentication.views import is_superuser_id
from master import services as master_services_emp



class EmployeeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'department']
        # extra_kwargs = {'permissions': {'required': False}}


class ListPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ['id', 'name']


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'designation']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    caste = serializers.SerializerMethodField('get_caste_name')
    department = serializers.SerializerMethodField('get_department_name')
    caste_category = serializers.SerializerMethodField('get_caste_cat_name')
    designation = serializers.SerializerMethodField('get_designation_name')
    gender = serializers.SerializerMethodField('get_gender')

    def get_department_name(self, obj):
        if obj:
            return {'id':obj.department.id, 'name':obj.department.name}

    def get_caste_name(self, obj):
        if obj:
            return {'id':obj.caste.id, 'name':obj.caste.caste}

    def get_caste_cat_name(self, obj):
        if obj:
            return {'id':obj.caste_category.id, 'name':obj.caste_category.category}

    def get_designation_name(self, obj):
        if obj:
            return {'id':obj.department.id, 'name':obj.department.name}

    def get_gender(self, obj):
        if obj:
            return {'id':obj.gender.id, 'name':obj.gender.gender}

    class Meta:
        model = EmployeeDetails
        fields = [
            'id',
            'employee_name',
            'employee_photo',
            'dob',
            'qualification',
            'caste',
            'caste_category',
            'martial_status',
            'father_husband_name',
            'father_husband_number',
            'present_address',
            'permanent_address',
            'contact_number',
            'email',
            'gender',
            'blood_group',
            'date_of_join',
            'work_experience',
            'class_group',
            'class_teacher',
            'department',
            'designation',
            'active']


class EmployeePostSerizlizer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetails
        fields = '__all__'



class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetails
        fields = ['id', 'employee_name', 'class_group']



class EmployeeAttendaceSerializer(serializers.Serializer):
    
    data = serializers.ListField(required=False)


class EmployeeAttendaceSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = '__all__'


class EmployeeInactiveSerializer(serializers.Serializer):
    employee_name = serializers.CharField(required=False)


class EmpoyeeProfileGet(serializers.ModelSerializer):

    class Meta:
        model = EmployeeDetails
        fields = '__all__'


class EmpAttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance()
        fields = '__all__'


    
class EmpModDepartmentSerizlizer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ['id', 'name']