from rest_framework import serializers
from master import models as master_models
from api_authentication.views import is_superuser_id
from rest_framework.validators import UniqueTogetherValidator

class ProfileSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = master_models.Profile
        fields = '__all__'

class ProfileCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = master_models.Profile
        exclude = ['is_active', 'created_by', 'created_on']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = master_models.Profile
        fields = ['trust_name', 'institution_name', 'address1', 'address2', 'phone_number', 'administrator', 'mobile_number', 'running_academic_start', 'running_academic_end', 'upcoming_academic_start', 'upcoming_academic_end', 'logo']

class ProfileDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = master_models.Profile
        fields = '__all__'
    
class RoomManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.RoomManagement
        fields = ['id']

class ClassGroupSerializer(serializers.ModelSerializer): 

    class Meta:
        model = master_models.ClassGroup
        fields = ['id','class_group']

class ClassGroupCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = master_models.ClassGroup
        fields = ['class_group']

class ClassGroupDetailSerializer(serializers.ModelSerializer): 

    class Meta:
        model = master_models.ClassGroup
        fields = ['id','class_group','created_on','created_by']

class ClassNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.ClassName
        fields = ['id','class_group','class_name','from_age','to_age']

class ClassNameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.ClassName
        fields = ['class_group','class_name','from_age','to_age']

class ClassNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.ClassName
        fields = ['class_group','class_name','from_age','to_age','created_on']

class ClassNameDetailSerializer(serializers.ModelSerializer): 
    class Meta:
        model = master_models.ClassName
        fields = ['id','class_group','class_name','from_age','to_age','created_on','created_by']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.Section
        fields = ['id','class_group','class_name','section_name']

class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.Section
        fields = ['class_group','class_name','section_name']

class SectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.Section
        fields = ['class_group','class_name', 'section_name', 'created_on']
    
class SectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.Section
        fields = ['id','class_group', 'class_name', 'section_name', 'created_on', 'created_by']  

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.CasteCategory
        fields = ['category']  

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.CasteCategory
        fields = ['category']

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.CasteCategory
        fields = ['category', 'created_on']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.CasteCategory
        fields = ['id', 'category','created_on', 'created_by']

class CasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = master_models.Caste
        fields = ['category', 'caste']

class CasteCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Caste
        fields = ['category', 'caste']
    
class CasteUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = master_models.Caste
        fields = ['category', 'caste', 'created_on']

class CasteDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Caste
        fields = ['id', 'category', 'caste', 'created_on', 'created_by']

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Subject
        fields = ['id', 'name', 'code', 'created_on', 'created_by']

class CreateOrUpdateSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Subject
        fields = ['name', 'code']

class GenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Gender
        fields = ['id', 'gender']

class QuotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Quota
        fields = ['id', 'name']

class ReligionSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.Religion
        fields = ['id', 'name']

class MotherTongueSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.MotherTongue
        fields = ['id', 'name']


class AcademicYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.AcademicYear
        fields = ['id','academic_year', 'start', 'end']
        
    # def validate(self, data):
       
    #     if data.get('start') == data.get('end'):
    #         raise serializers.ValidationError('Start and end date should be different')
        
    #     if data.get('start') > data.get('end'):
    #         raise serializers.ValidationError('Start date cannot be greater than end data')
        
    #     if master_models.AcademicYear.objects.filter(academic_year = data['academic_year']).exists():
    #         raise serializers.ValidationError('Academic year already exists')
       
    #     return data

class StudentRegisterFieldsSerializer(serializers.ModelSerializer):

    class Meta:
        model = master_models.StudentRegisterFields
        fields = ['id', 'field','is_mandatory']
