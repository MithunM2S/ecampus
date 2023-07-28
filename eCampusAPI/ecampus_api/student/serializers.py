from rest_framework import serializers
from student.models import *
from preadmission.models import Application
from master import services
from student.validators import *
from django.db.models import F
import ast
from master import services as master_services
from preadmission.models import Application as preadmission_application
class StudentDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        # fields = '__all__'
        exclude = ['uploaded_on', ]

class StudentApplicationDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        exclude = ['id']

class ParentDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ParentDetails
        exclude = ['student', 'id']

class ProfileSerializer(serializers.ModelSerializer):
    parent_details = ParentDetailsSerializer()

    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['gender'] = services.get_related(instance.gender, 'gender')
        response['class_name'] = services.get_related(instance.class_name, 'class_name') 
        response['section'] = services.get_related(instance.section, 'section_name') 
        response['quota'] = services.get_related(instance.quota, 'name') 
        response['religion'] = services.get_related(instance.religion, 'name') 
        response['mother_tongue'] = services.get_related(instance.mother_tongue, 'name') 
        response['caste_category'] = services.get_related(instance.caste_category, 'category') 
        response['caste'] = services.get_related(instance.caste, 'caste')
        return response


class AdmissionSerializer(serializers.ModelSerializer):
    parent_details = ParentDetailsSerializer()

    class Meta:
        model = Profile
        exclude = ['admission_number', 'admission_on', 'created_by', 'created_on']
    
    def validate(self, validated_data):
        application_id = validated_data.get('application_id', None)
        parent_details = validated_data.get('parent_details', None)
        if not Application.objects.filter(id=application_id, is_applied=True, is_docs_verified=True).exists():
            raise serializers.ValidationError({'application_id': 'Invalid application id'})
        admission_academic_year = validated_data.get('admission_academic_year')
        if admission_academic_year != services.get_academic_years_key_value('running')[0]:
            raise serializers.ValidationError({'admission_academic_year': 'Aadmission academic year not exists'})
        if not parent_details.get(validated_data.get('primary_contact', None)+"_mobile", None):
            raise serializers.ValidationError({'primary_contact':"Required " + validated_data.get('primary_contact', None) +" mobile number"})
        return validated_data

    def create(self, validated_data):
        parent_data = validated_data.pop('parent_details')
        instance = super().create(validated_data)
        if parent_data:
            serializer = ParentDetailsSerializer(data=parent_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(student=instance)
        return instance

class ProfileEditSerializer(serializers.ModelSerializer):
    parent_details = ParentDetailsSerializer()

    class Meta:
        model = Profile
        exclude = ['application_id', 'admission_number', 'admission_academic_year', 'admission_on', 'student_id', 'created_by', 'created_on']

    def validate(self, validated_data):
        parent_details = validated_data.get('parent_details', None)
        if not parent_details.get(validated_data.get('primary_contact', None)+"_mobile", None):
            raise serializers.ValidationError({'primary_contact':"Required " + validated_data.get('primary_contact', None) +" mobile number"})
        return validated_data

    def update(self, instance, validated_data):
        parent_data = validated_data.pop('parent_details')
        instance = super().update(instance, validated_data)
        if parent_data:
            parent_info = ParentDetailsSerializer(
            instance=instance.parent_details,
            data=parent_data,
            )
            parent_info.is_valid()
            parent_info.save()
        return instance

class UpdateProfilePictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['picture']

    def validate(self, validated_data):
        picture = validated_data.get('picture', None)
        if not picture:
            raise serializers.ValidationError({'picture':"Profile picture required"})
        return validated_data


class StudentStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['is_active']


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = '__all__'
        
    def to_representation(self, instance): # Need to look
        response = super().to_representation(instance)
        if(instance.presence):
            response['presence'] = self.get_attendance_students(instance.presence)
        if(instance.absence):
            response['absence'] = self.get_attendance_students(instance.absence)
        response['class_group'] = master_services.get_related(instance.class_group, 'class_group')
        response['class_name'] = master_services.get_related(instance.class_name, 'class_name')
        response['section'] = master_services.get_related(instance.section, 'section_name')
        response['session'] = master_services.get_related(instance.session, 'name')
        return response

    def get_attendance_students(self, ids):
        return Profile.objects.values(
                studentId=F('student_id'),
                name=F('first_name')
                ).filter(
                    id__in=ast.literal_eval(ids)
                )

class AttendanceCreateOrUpdateSerializer(serializers.ModelSerializer):
    presence = serializers.ListField()
    absence = serializers.ListField()
    
    class Meta:
        model = Attendance
        exclude = ['created_by']

    def validate(self, validate_data):
        error, error_message = AttendanceValidator(validate_data).validator()
        if error:
            raise serializers.ValidationError(error_message)
        return validate_data


'''
Add existing student preadmission_application model serializer

'''


class AddExistingStudentApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = preadmission_application
        exclude = ['created_on', 'created_by', 'reference_number', 'docs', 'mode', 'query', 'email_address', 'student_name']


class AddExistingStudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        exclude = ['application_id', 'admission_on', 'created_by', 'created_on']    
        
        