from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from preadmission import serializers
from preadmission.models import Application
from api_authentication.permissions import HasOrganizationAPIKey
from rest_framework.permissions import AllowAny, IsAuthenticated
from employee.permissions import EmployeeHasPermission
from base.views import MultipleFieldLookupMixin
from student.models import Document
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from django.conf import settings
from master import services
from django.db import transaction
from django.db.models import Q
from master.models import Repo,ClassName
from django_filters.rest_framework import DjangoFilterBackend
from preadmission.services import PreadmissionCountService
from student.services import ProfileCountService
from rest_framework import filters
from master import url_shortner

class ApplicationMixin(viewsets.ModelViewSet):
    
    queryset = Application.objects.all()
    serializer_class = serializers.ApplicationCreateSerializer

class ApplicationViewSet(ApplicationMixin):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
                'is_verified',
                'is_applied',
                'is_docs_verified',
                'gender',
                'academic_year',
                'class_name',
                'existing_parent',
                'mode',
                'is_admitted',
    ]
    search_fields = [
                'student_name',
                'father_name',
                'father_mobile',
                'mother_name',
                'mother_mobile',
                'id',
                'dob',
                'email_address',
    ]
    ordering_fields = [
        'created_on',
        'academic_year',
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ApplicationCreateSerializer
        if self.action == 'update':
            return serializers.ApplicationUpdateSerializer
        if self.action == 'list':
            return serializers.ApplicationListSerializer
        if self.action == 'retrieve':
            return serializers.ApplicationListSerializer
        return super(serializers.ApplicationCreateSerializer, self).get_serializer_class()

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve':
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.filter(application_token=self.request.GET.get('application_token', None))
        if self.action == 'list':
            query_academic_year = self.request.query_params.get('academic_year', None)
            if not query_academic_year:
                queryset = queryset.filter(academic_year=services.get_academic_years_key_value('running')[0])
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user  = self.request.user.id
            mode = False
            
        else:
            user = 0
            mode= True
        serializer.save(application_token=services.unique_token(), mode=mode, created_by=user)
        class_name_details = ClassName.objects.get(id=serializer.data['class_name'])
        message ="Dear Sir/Madam, Thank you for your enquiry regarding the admission of your ward "+serializer.data['student_name']+" for "+class_name_details.class_name+". After verification you will receive a message from our Team. Reference Number "+str(serializer.data['id'])+" Regards, "+settings.SCHOOL_NAME
        services.send_sms(serializer.data[serializer.data['primary_contact_person']+"_mobile"], message)
        # print(message,'create')
        

    def perform_update(self, serializer):
        enquiry_reference_numer = None
        is_verified = int(self.request.data.get('is_verified', None))
        form_reference_number = self.request.data.get('reference_number', None)
        if is_verified == True:
            aid= self.get_object().id
            year =self.request.data.get('academic_year', None)
            unique_token = self.get_object().application_token
            # mobile_number = self.request.data['contact_number']
            mobile_number = self.request.data[self.request.data['primary_contact_person']+"_mobile"]
            with transaction.atomic():
                repo = Repo.objects.select_for_update().get(academic_year=year)
                new_reference_number = repo.reference_number + 1
                repo.reference_number = new_reference_number
                repo.save()
            reference_number =  year[2:4] + year[-2:] + "{:02d}".format(new_reference_number)
            serializer.save(reference_number=reference_number)
            url =  settings.APPLICATION_DOMAIN+str(aid)+"?application_token="+unique_token
            url_short = url_shortner.make_shorten(url)
            # message = "Reference Number - " + reference_number + " Application link - " + settings.APPLICATION_DOMAIN + 'page/submit/application?token='  + str(unique_token)
            message ="Dear Sir / Madam, Your enquiry form is verified by the admission team. Kindly click on below link to fill the Application Form and upload all required documents. "+url_short+" Reference Number " + reference_number +" Regards, "+settings.SCHOOL_NAME
            # print(message,'update')
            services.send_sms(mobile_number, message)
        else:
            pass
            serializer.save()

class SubmitDocsViewSet(MultipleFieldLookupMixin, ApplicationMixin):
    lookup_fields = ('id', 'application_token')
    serializer_class = serializers.SubmitApplicationSerializer
    # parser_classes = [FormParser, MultiPartParser,]
    permission_classes = [AllowAny, HasOrganizationAPIKey]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def perform_update(self, serializer):
        student_photo = self.request.FILES.get('student_photo', None)
        birth_certificate = self.request.FILES.get('birth_certificate', None)
        tc = self.request.FILES.get('tc', None)
        photo = self.request.FILES.get('photo', None)
        request_documents = {}
        if self.get_object().is_verified:
            if self.get_object().docs:
                doc_id = self.get_object().docs.id
            else:
                doc_id = None
            if student_photo:
                request_documents['student_photo'] = student_photo
            if birth_certificate:
                request_documents['birth_certificate'] = birth_certificate
            if tc:
                request_documents['tc'] = tc
            if photo:
                request_documents['photo'] = photo
            obj, student_document = Document.objects.update_or_create(id=doc_id, defaults=request_documents)
            application_instance = serializer.save(docs=obj, is_applied=True)

class ApproveOrRejectDoc(MultipleFieldLookupMixin, ApplicationMixin):
    lookup_fields = ('id', 'application_token')
    
    serializer_class = serializers.ApproveOrRejectDocSerializer

    def perform_update(self, serializer):
        # print("lookup ",self.lookup_fields)
        is_docs_verified = self.request.data.get('is_docs_verified')
        self_obj = self.get_object()
        class_name_details = ClassName.objects.get(id=self_obj.class_name_id)
        contact_person = self_obj.primary_contact_person
        contact_number = getattr(self_obj, contact_person + "_mobile")
        if is_docs_verified == False and self_obj.is_applied == True:
            app_link_token = services.unique_token()
            serializer.save(is_applied=False, application_token=app_link_token)
            # url =  settings.APPLICATION_DOMAIN+str(self_obj.id)
            # url = "http://creaxiotechnologies.com/pages/submit-application/700?application_token=7c31c547e899e4d3edec86f0123793fa0b788264e564860dbfbc8c5d5bb70167"
            url =  settings.APPLICATION_DOMAIN+"/pages/submit-application/"+str(self_obj.id)+"?application_token="+self_obj.application_token
            url_short = url_shortner.make_shorten(url)
            message = "Dear Sir / Madam, Your uploaded document has been rejected due to "+self_obj.query+", Please upload the documents again. Kindly click on below link to upload the documents. " +settings.APPLICATION_DOMAIN+" Reference Number "+self_obj.reference_number+" Regards, "+settings.SCHOOL_NAME
            # # print(message)

        else:
            #message = "Dear Sir/Madam, Thank you for your enquiry regarding the admission of your ward "+self_obj.student_name+" for "+class_name_details.class_name+". After verification you will receive a message from our Team. Reference Number "+self_obj.reference_number+" Regards, creaxio school - Creaxio"
            message = "Dear Sir/Madam, Thank you for your enquiry regarding the admission of your ward "+self_obj.student_name+" for "+class_name_details.class_name+". After verification you will receive a message from our Team. Reference Number "+self_obj.reference_number+" Regards, creaxio school - Creaxio"
            # print(message,'accept')
            serializer.save(is_docs_verified=True)
        services.send_sms(contact_number, message)

#  DashboardService

class DashboardService(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationAPIKey]

    def get(self, request):
        academic_year = request.GET.get('academicYear', None)  
        dashboard_service_object = PreadmissionCountService(academic_year)
        profile_service = ProfileCountService()
        dashboard_service = {
            "cards": dashboard_service_object.get_card_count('card_name', 'mode'),
            'class_group_wise_student_count': dashboard_service_object.get_class_group_wise_student_count(),
            'class_wise_student_count': dashboard_service_object.get_class_wise_student_count(),
            'online_enquiry_count': dashboard_service_object.get_online_enquiry_count(),
            'offline_enquiry_count': dashboard_service_object.get_offline_enquiry_count(),
            'yearly_admission_count': profile_service.get_yearly_admission_count()
            }
        return Response(dashboard_service)
