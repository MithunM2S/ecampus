# from asyncio.windows_events import NULL
from itertools import count
import numpy as np
from rest_framework import serializers
from zmq import has
from fee import models
from master import services
from django.db.models import Q, F, Sum, Count
from student import models as student_models
import pandas as pd

class FeeTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeType
    fields = ['fee_type', 'fee_type_name']


class FeeTypeCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeType
    fields = ['fee_type', 'fee_type_name']


class FeeTypeUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeType
    fields = ['fee_type', 'fee_type_name', 'created_on']


class FeeTypeDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeType
    fields = ['id', 'fee_type', 'fee_type_name', 'created_on', 'created_by']


class FeeCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeCategory
    exclude = ['id', 'created_by', 'created_on']


class FeeCategoryUpdateSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = models.FeeCategory
    exclude = ['id', 'created_by', 'created_on']
    # extra_kwargs = {'logo': {'required': True}}


class FeeCategoryDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeCategory
    fields = '__all__'


class FeeToClassSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeToClass
    exclude = ['created_on', 'created_by']

class FeeToClassCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeToClass
    exclude = ['created_on', 'created_by']

  def validate(self, validated_data):
    if not services.check_academic_year(validated_data.get('academic_year')):
      raise serializers.ValidationError({'admission_academic_year': 'Academic year not exists'})
    if validated_data.get('class_name', None) and validated_data.get('student', None):
      raise serializers.ValidationError({'class_name': "Can't be both class and Student"})
    isUniqueFeeToClass = models.FeeToClass.objects.filter(
      quota=validated_data.get('quota', None),
      fee_category=validated_data.get('fee_category', None),
      fee_type=validated_data.get('fee_type', None),
      academic_year=validated_data.get('academic_year', None),
    )
    if validated_data.get('class_name', None):
      isUniqueFeeToClass = isUniqueFeeToClass.filter(class_name=validated_data.get('class_name', None))
    if validated_data.get('student', None):
      isUniqueFeeToClass = isUniqueFeeToClass.filter(student=validated_data.get('student', None))
    if validated_data.get('section', None):
      isUniqueFeeToClass = isUniqueFeeToClass.filter(section=validated_data.get('section', None))
    isUniqueFeeToClass.exists()
    if isUniqueFeeToClass:
        raise serializers.ValidationError({'student_id': "Already Fee to Class added."})
    return validated_data


class FeeToClassUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeToClass
    exclude = ['created_by', 'created_on']

  def validate(self, validated_data):
    if not services.check_academic_year(validated_data.get('academic_year')):
      raise serializers.ValidationError({'admission_academic_year': 'Academic year not exists'})
    return validated_data





class FeeToClassDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeToClass
    fields = '__all__'

  def to_representation(self, instance):
      response = super().to_representation(instance)
      if response['student']:
        extra_student_args = ['student_id'] 
        response['student'] = services.get_related(instance.student, 'first_name', extra_student_args)
      response['class_name'] = services.get_related(instance.class_name, 'class_name')
      response['section'] = services.get_related(instance.section, 'section_name')
      response['fee_category'] = services.get_related(instance.fee_category, 'fee_category')
      response['fee_type'] = services.get_related(instance.fee_type, 'fee_type')
      response['fee_type_name'] = instance.fee_type.fee_type_name
      response['quota'] = services.get_related(instance.quota, 'name')
      return response


class PaymentModeSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PaymentMode
    fields = ['name']


class PaymentModeDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PaymentMode
    fields = '__all__'


class FeeConcessionSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeConcession
    fields = '__all__'


class CreateFeeConcessionSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeConcession
    fields = ['concession_amount', 'student_id', 'academic_year', 'fee_to_class']


  def validate(self, validated_data):
    if not services.check_academic_year(validated_data.get('academic_year')):
      raise serializers.ValidationError({'admission_academic_year': 'Academic year not exists'})

    isUnusedConcession = models.FeeConcession.objects.filter(
      student_id=validated_data['student_id'],
      fee_to_class=validated_data['fee_to_class'],
      academic_year=validated_data['academic_year'],
      is_valid=True
      ).exists()
    if isUnusedConcession:
        raise serializers.ValidationError({'student_id': "Already concession amout added."})
    return validated_data

class CreateFeeCollectionSerializer(serializers.ModelSerializer):

  fee_denomination = serializers.JSONField()

  class Meta:
    model = models.FeeCollection
    exclude = ['created_on', 'created_by', 'balance_amount', 'total_payable_amount']

  def validate(self, validated_data):
    if not services.check_academic_year(validated_data.get('academic_year')):
      raise serializers.ValidationError({'admission_academic_year': 'Academic year not exists'})
    return validated_data

class FeeCollectionSerializer(serializers.ModelSerializer):

  class Meta:
    model = models.FeeCollection
    fields = '__all__'

  def to_representation(self, instance):
      response = super().to_representation(instance)
      del response['student_id']
      extra_student_args = ['student_id'] 
      response['student'] = services.get_related(instance.student_id, 'first_name', extra_student_args)
      response['payment_mode'] = services.get_related(instance.payment_mode, 'name')
      return response


class FeeMasterCollectionSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeMasterCollection
    fields = '__all__'

  def to_representation(self, instance):
      response = super().to_representation(instance)
      # for cid in instance.fee_collections.split(","):
      response['fee_collections'] = models.FeeCollection.objects.select_related('fee_to_class', 'fee_to_class__fee_type').values(
        feeId=F('id'),
        feeName=F('fee_to_class__fee_type__fee_type_name'),
        paidAmount=F('paid_amount'),
        academicYear=F('academic_year')
        ).filter(
          id__in=[cid for cid in instance.fee_collections.split(",")]
      )
      # print(response['fee_collections'])
      # response['fee_collections'] = [int(cid) for cid in instance.fee_collections.split(",")]
      response['bill_number'] = instance.bill_number
      response['student'] = student_models.ParentDetails.objects.select_related('student', 'student__class_name', 'student__section').values(
        studentName=F('student__first_name'),
        className=F('student__class_name__class_name'),
        sectionName=F('student__section__section_name'),
        fatherName=F('father_name'),
        studentId=F('student__student_id')
        ).get(student=instance.student)
      # services.get_related(instance.student, 'first_name')
      response['payment_mode'] = services.get_related(instance.payment_mode, 'name')
      response['fee_category'] = services.get_related_feecategory(instance.fee_category, 'fee_category','company_name')
      
      # return response

      return response


class DailyReportSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.FeeMasterCollection
    fields = '__all__'

  def to_representation(self, instance):
     
      response = super().to_representation(instance)
      response['fee_collections'] = models.FeeCollection.objects.select_related('fee_to_class', 'fee_to_class__fee_type').values(
        feeId=F('id'),
        feeName=F('fee_to_class__fee_type__fee_type_name'),
        paidAmount=F('paid_amount'),
        academicYear=F('academic_year')
        ).filter(
          id__in=[cid for cid in instance.fee_collections.split(",")]
      )
      response['bill_number'] = instance.bill_number
      response['student'] = student_models.ParentDetails.objects.select_related('student', 'student__class_name', 'student__section').values(
        studentName=F('student__first_name'),
        className=F('student__class_name__class_name'),
        sectionName=F('student__section__section_name'),
        fatherName=F('father_name'),
        studentId=F('student__student_id')
        ).get(student=instance.student_id)
      response['payment_mode'] = services.get_related(instance.payment_mode, 'name')
      response['fee_category'] = services.get_related_feecategory(instance.fee_category, 'fee_category','company_name')
      # for cid in instance.fee_category:
      # Data=models.FeeCategory.objects.all().filter(fee_category=instance.fee_category).values('id','fee_category','company_name','logo')
      # if len(Data) >= 1:
      #       for item in Data:
      #           newitem = dict(item)
      #           print(Data)
      # response['fee_category'] = newitem
      
      return response


class StudentSerializer(serializers.ModelSerializer):
  class Meta:
    model = student_models.Profile
    fields = ('id', 'section', 'class_name')
