from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, mixins
# from eCampusAPI.ecampus_api.master.models import Profile
from student import models as student_model, serializers as student_serializer
from rest_framework import response, status
from django.db import transaction, IntegrityError
from master.models import Repo, ClassName, RepoClass
from master.services import get_institution_prefix, unique_token
from django_filters.rest_framework import DjangoFilterBackend
from student.services import ProfileCountService, get_student_state, delete_null_keys_if_present
from rest_framework.views import APIView
from api_authentication.permissions import HasOrganizationAPIKey
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from preadmission.models import Application
from rest_framework import filters
from django.db.models import Q, F
from master import services


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = student_model.Profile.objects.all().filter()
    serializer_class = student_serializer.ProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
                'admission_academic_year',
                'gender',
                'class_name',
                'section',
                'combination',
                'quota',
                'caste_category',
                'caste',
                'is_active',
                
    ]
    search_fields = [
                'admission_number',
                # 'admission_on',
                'student_id',
                'first_name',
                'dob',

                # 'student_mobile',
                # 'current_address',
                # 'father_name',
                # 'father_mobile',
                # 'mother_name',
                # 'mother_mobile',
                # 'guardian_name',
                # 'guardian_mobile',
    ]
    
    ordering_fields = [
        'created_on',
        'admission_academic_year',
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return student_serializer.AdmissionSerializer
        elif self.action == 'update':
            return student_serializer.ProfileEditSerializer
        else:
            return super(ProfileViewSet, self).get_serializer_class()
    
    def perform_create(self, serializer):
        admission_academic_year = self.request.data.get('admission_academic_year', None)
        class_id =  self.request.data.get('class_name', None)
        application_id =  self.request.data.get('application_id', None)
        class_instance = ClassName.objects.get(id=class_id)
        with transaction.atomic():
            repo = Repo.objects.select_for_update().get(admission_academic_year=admission_academic_year)
            repo_new_admission_number = repo.admission_number + 1
            repo.admission_number = repo_new_admission_number
            repo.save()
        # with transaction.atomic():
        #     class_obj = RepoClass.objects.get(admission_academic_year=admission_academic_year, cid=class_id)
        #     class_code = class_instance.class_code
        #     student_id = (class_obj.max_strength - class_obj.available_strength) + 1
        #     class_obj.available_strength = class_obj.available_strength - 1
        #     class_obj.save()
        admission_number =  admission_academic_year[2:4] + admission_academic_year[-2:] + "{:02d}".format(repo_new_admission_number)
        # new_student_id = get_institution_prefix() + str(admission_academic_year[2:4]) + str(class_code) + str("{:02d}".format(student_id))
        new_student_id = 1000 + self.queryset.count() + 1
        admission_academic_year[0:2]
        student = serializer.save(admission_number=admission_number, student_id=new_student_id, created_by=self.request.user.id)
        student_history = student_model.History.objects.create(student=student, to_class=class_id, to_academic_year=admission_academic_year)
        student_instance = student_model.Profile.objects.get(admission_number=admission_number)
        if application_id:
            Application.objects.filter(id=application_id).update(is_admitted=True)
            instance = Application.objects.get(id=student_instance.application_id)
            message = "Dear Parent, Thank you for choosing our school. Admission process of your ward "+student_instance.first_name+" for "+class_instance.class_name+" is completed successfully. We wish "+student_instance.first_name+" to have a prosperous career. Student ID "+student_instance.student_id+" Regards, "+settings.SCHOOL_NAME
            if instance.primary_contact_person == 'father': mobile=instance.father_mobile #for takinfg mobile number
            else : mobile=instance.mother_mobile
            print(message)
            services.send_sms(mobile, message)


#  Student Dashboard Service

class DashboardService(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationAPIKey]

    def get(self, request):
        admission_academic_year = request.GET.get('admissionAcademicYear', None)
        profile_count_service = ProfileCountService(admission_academic_year)
        student_dashboard_service = {
            'cards': profile_count_service.get_cards_count(),
            'class_group_wise_student_count': profile_count_service.get_class_group_wise_student_count(),
            'class_wise_student_count': profile_count_service.get_class_wise_student_count(),
            'section_wise_student_count': profile_count_service.get_section_wise_student_count(),
            }
        return response.Response(student_dashboard_service)


# Update Profile Picture

class UpdateProfilePicture(viewsets.ModelViewSet):
    queryset = student_model.Profile.objects.all()
    serializer_class = student_serializer.UpdateProfilePictureSerializer
    http_method_names = ['put']


# Search Student API

class SearchStudent(APIView):
    permission_classes = [HasOrganizationAPIKey, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_text = request.GET.get('search-text', None)
        status = request.GET.get('status', None)
        search_response = {}
        if search_text:
            queryset = student_model.ParentDetails.objects.select_related('student', 'student__class_name', 'student__section').values(Id=F('student__id'), studentName=F('student__first_name'),
                                                                                     studentId=F('student__student_id'),
                                                                                     status=F('student__is_active'),
                                                                                     className=F(
                                                                                       'student__class_name__class_name'),
                                                                                     sectionName=F(
                                                                                       'student__section__section_name'),
                                                                                     fatherName=F('father_name'),
                                                                                     fatherMobile=F('father_mobile'),
                                                                                     quotaId=F('student__quota'),
                                                                                     ).filter(Q(father_name__icontains=search_text) | Q(father_mobile=search_text) | Q(student__student_id=search_text)
                                                                                    | Q(student__first_name__icontains=search_text) | Q(student__student_id=search_text) | Q(student__student_mobile=search_text))
        
            
            if status == 'active':
                queryset = queryset.filter(student__is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(student__is_active=False)
            elif status == 'all':
                pass
            else:
                queryset = queryset.filter(student__is_active=True)
            search_response = queryset
            for row, value in enumerate(search_response):
                search_response[row]['studentType'] = get_student_state(value.get('Id'))

        return response.Response(search_response)

# Student profile state
class StudentStatus(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = student_model.Profile.objects.all()
    serializer_class = student_serializer.StudentStatusSerializer
    http_method_names = ['put']


#Attendance view set
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = student_serializer.AttendanceSerializer
    queryset = student_model.Attendance.objects.all()
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'class_group':['exact'],
        'class_name':['exact'],
        'section':['exact'],
        'session':['exact'],
        'attendance_date':['gte', 'lte', 'exact']
    }

    def get_logged_user_id(self):
        return self.request.user.id

    def perform_create(self, serializer):
        serializer.save(created_by=self.get_logged_user_id())
 
    def perform_update(self, serializer):
        serializer.save(serializer.save(created_by=self.get_logged_user_id()))

    def get_serializer(self, *args, **kwargs):
      if "data" in kwargs:
        self.request_data = kwargs["data"]
        # check if many is required
        if isinstance(self.request_data, list):
            kwargs["many"] = True
      return super(AttendanceViewSet, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return student_serializer.AttendanceCreateOrUpdateSerializer
        return super(AttendanceViewSet, self).get_serializer_class()


class AddExistingStudent(APIView):

    '''
    Add Existing Student details
    '''
    student_profile_query_set = student_model.Profile.objects.all()
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        data = delete_null_keys_if_present(request.data)
        application_serializer = student_serializer.AddExistingStudentApplicationSerializer(data=data, partial=True) #Application Serializer

        try:
            with transaction.atomic():
                
                if application_serializer.is_valid():
                    application_token = unique_token() 
                    if data['primary_contact_person'] == 'father':
                        email_address = data['father_email'] #email id intial to father if primary contact is mother it will be set to mother
                    else:
                        email_address = data['mother_email']
                    application_instance = application_serializer.save(application_token=application_token, 
                                                                       email_address=email_address, 
                                                                       student_name=data['first_name'],
                                                                       is_verified=True,
                                                                       is_docs_verified=True,
                                                                       mode=False 
                                                                       )
                    application_id = application_instance.id #phase 1 is over
                    print('phase 1 is over')
                    #once the application is created we have to create student profile
                    profile_serializer = student_serializer.AddExistingStudentProfileSerializer(data=data, partial=True)
                    
                    # print(profile_serializer)
                    if profile_serializer.is_valid():
                        # print(profile_serializer)
                       
                        student_id = 1000 + self.student_profile_query_set.count() + 1

                        if ('admission_number' in data) and (self.student_profile_query_set.filter(admission_number=int(data['admission_number'])).exists()):
                            transaction.set_rollback(True)
                            return response.Response({'detail' : 'student admission number already exist'}, status=409)
                        
                        profile_instance = profile_serializer.save(application_id=application_id, student_id=student_id, 
                                                                #    admission_number=data['admission_number'], 
                                                                   admission_academic_year=data['academic_year'],
                                                                   primary_contact=data['primary_contact_person'])
                        #phase 2 is over now have to add have to map parent to student
                        print('phase 2 is over') 
                        student_foreign_key_id = profile_instance.id
                        parent_serializer = student_serializer.ParentDetailsSerializer(data=data, partial=True)

                        if parent_serializer.is_valid():
                            parent_instance = parent_serializer.save(student_id=student_foreign_key_id)
                            #phase 3 is over now we have to add data to student history
                            student_model.History.objects.create(student=profile_instance, from_class=data['class_name'], from_academic_year=data['academic_year'])
                            return response.Response({"message" : "student added successfully", "student_id" : student_id}, status=200)
                            
                        else:
                            data = {'message': parent_serializer.errors}
                            # print(data)
                            return response.Response(parent_serializer.errors, status=422)
                    else:
                        print(profile_serializer.errors)
                        return response.Response(profile_serializer.errors, status=422)
                else:
                    print(application_serializer.errors)
                    return response.Response(application_serializer.errors, status=422) 
                    
                
        except IntegrityError as e:
            transaction.set_rollback(True)
            return response.Response({'detail' : 'student admission number already exist'}, status=409)
        except Exception as e:
            print(e)
            return response.Response({'message': 'some error has occured'}, status=422)    


