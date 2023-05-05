from django.contrib.auth.models import Group as Role, Permission
from rest_framework import serializers
from .models import AttendanceTracker
from django.conf import settings
from api_authentication.views import is_superuser_id
from django.db.models import F
from master import services as master_services
from student.models import Profile
from django_filters.rest_framework import DjangoFilterBackend


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceTracker()
        fields = ['section']
        
    def to_representation(self, instance): # Need to look
        response = super().to_representation(instance)
        if(instance.presence):
            response['presence'] = Profile.objects.values(studentId=F('student_id'),name=F('first_name')).filter(id__in=instance.presence.split(','))
        if(instance.absence):
            response['absence'] = Profile.objects.values(studentId=F('student_id'),name=F('first_name')).filter(id__in=instance.absence.split(','))
        response['class_group'] = master_services.get_related(instance.class_group, 'class_group')
        response['class_name'] = master_services.get_related(instance.class_name, 'class_name')
        response['section'] = master_services.get_related(instance.section, 'section_name')
        response['session'] = master_services.get_related(instance.session, 'session_name')
        return response
        
class validateSerializer():
    
    def customValidate(self,validate_data):
        presenceID = validate_data['presence']
        absenceID = validate_data['absence']
        ## Empty Validation ###
        if len(presenceID) == 0 and len(absenceID) == 0:
            raise serializers.ValidationError('Error : Presence and Absence id list cannot be empty!')
        elif len(presenceID) > 0 and len(absenceID) > 0:
            #ids = [int(i) for i in presenceID.split(',')]
            #ids1 = [int(i) for i in absenceID.split(',')]
            match_list = list(set(presenceID) & set(absenceID))
            if(len(match_list) >= 1):
                match_list = [str(i) for i in match_list]
                raise serializers.ValidationError('Found Duplicate Id in both Presence and Absence ID list : '+str(','.join(match_list)))
        count = Profile.objects.filter(class_group_id=validate_data['class_group'],class_name_id=validate_data['class_name'],section_id=validate_data['section']).count()
        students_strgenth = presenceID + absenceID
        #students_strgenth = re.sub(r'^\s*?\,','',students_strgenth)
        #students_strgenth = re.sub(r'\s*?\,$','',students_strgenth)
        #print(count,students_strgenth)
        if(len(students_strgenth) != count):
            raise serializers.ValidationError('Error : Sum of Presence and absence ids are not matched with Total student strgenth')
        
        if len(presenceID) > 0:
            self.listcompare(presenceID,'Presence',validate_data)
            
        if len(absenceID) > 0:
            self.listcompare(absenceID, 'Absence',validate_data)
        
        return validate_data
    
    def listcompare(self,list_var,preciseattendance,validate_data):
        get_list_db=Profile.objects.values('id').filter(id__in=list_var,class_group_id=validate_data['class_group'],class_name_id=validate_data['class_name'],section_id=validate_data['section'])
        get_list = [i['id'] for i in get_list_db]
        list_var = list(set(list_var)-set(get_list))
        if(len(list_var) >=1):
            raise serializers.ValidationError(str(preciseattendance)+' list - Student IDs are invalid:' +str(list_var))

class AttendanceCreateSerializer(serializers.ModelSerializer):
    presence = serializers.ListField()
    absence = serializers.ListField()
    
    class Meta:
        model = AttendanceTracker
        exclude = ['created_on']
        
    def validate(self, validate_data):
        return_value = validateSerializer().customValidate(validate_data)
        return return_value
    
class AttendanceUpdateSerializer(serializers.ModelSerializer):
    presence = serializers.JSONField()
    absence = serializers.JSONField()
    
    class Meta:
        model = AttendanceTracker
        fields = "__all__"

    def validate(self, validate_data):
        return_value = validateSerializer().customValidate(validate_data)
        return return_value
    
        
    def to_representation(self, instance): # Need to look
        response = super().to_representation(instance)
        if(instance.presence):
            response['presence'] = Profile.objects.values(studentId=F('student_id'),name=F('first_name')).filter(id__in=instance.presence.split(','))
        if(instance.absence):
            response['absence'] = Profile.objects.values(studentId=F('student_id'),name=F('first_name')).filter(id__in=instance.absence.split(','))
        response['class_group'] = master_services.get_related(instance.class_group, 'class_group')
        response['class_name'] = master_services.get_related(instance.class_name, 'class_name')
        response['section'] = master_services.get_related(instance.section, 'section_name')
        response['session'] = master_services.get_related(instance.session, 'session_name')
        return response



class AttendanceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceTracker()
        fields = ['section']

    def to_representation(self, instance): # Need to look
        response = super().to_representation(instance)
        response['id'] = instance.id
        if(instance.presence):
            presence = Profile.objects.values('student_id','first_name','id').filter(id__in=instance.presence.split(','))
        if(instance.absence):
            absence = Profile.objects.values('student_id','first_name','id').filter(id__in=instance.absence.split(','))
        student_lists = []
        if(instance.presence):
            for i in presence:
                i['status'] = 'p'
                student_lists.append(i)
        if(instance.absence):
            for i in absence:
                i['status'] = 'ab'
                student_lists.append(i)

        response['student_lists'] = student_lists
        response['class_group'] = master_services.get_related(instance.class_group, 'class_group')
        response['class_name'] = master_services.get_related(instance.class_name, 'class_name')
        response['section'] = master_services.get_related(instance.section, 'section_name')
        response['session'] = master_services.get_related(instance.session, 'session_name')
        return response
