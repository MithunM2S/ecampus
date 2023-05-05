from django.shortcuts import render
from sendsms import models as sms_models
from sendsms import serializers as sms_serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, mixins
from student import models as student_models
from django.db.models import Q, F, Count
from master.models import GroupConcat
from master import services as master_services
from sendsms.services import TextLocalServices
from rest_framework import response
from rest_framework import status
from employee import models as employee_models
import ast
from rest_framework.views import APIView
from api_authentication.permissions import HasOrganizationAPIKey
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.

class BaseSmsService(TextLocalServices):

    def get_client_request_data(self, serializer_data):
        client_request_data = {}
        student_field_data = serializer_data.get('student_field_data', None)
        class_field_data = serializer_data.get('class_field_data', None)
        class_group_field_data = serializer_data.get('class_group_field_data', None)
        section_field_data = serializer_data.get('section_field_data', None)
        addtional_numbers_field_data = serializer_data.get('addtional_numbers_field_data', [])
        client_request_data = {}
        recipients = [] + addtional_numbers_field_data
        profile_queryset = student_models.Profile.objects.filter(
            Q(id__in=student_field_data) |
            Q(class_name__in=class_field_data) |
            Q(class_group__in=class_group_field_data) |
            Q(section__in=section_field_data)).values(
                'primary_contact').annotate(
                ids_count=Count('primary_contact'), ids=GroupConcat('id')).order_by()
        for row in profile_queryset:
            field_name = row.get('primary_contact') + '_mobile'
            ids = row.get('ids').split(",")
            contact_details = student_models.ParentDetails.objects.filter(
                student_id__in=ids).values(
                    mobile_number=F(field_name),
                    profile_id=F('student_id'))
            for detail in contact_details:
                key = detail.get('profile_id', None)
                value = detail.get('mobile_number', None)
                client_request_data[str(key)] = value
                if value:
                    recipients.append(int(value))

        # client_request_data = {
        #     "1808": 9964116553,
        #     "1749": 855365170,
        #     "1807": 996411655
        # }
        # recipients = [9964116553, 855365170, 996411655]

        return client_request_data, recipients

    def get_sms_service(self, tracker_id, recipients, template):
        vendor_reposnse = self.send_sms(recipients, template)
        if not vendor_reposnse:
            return False, False, False
        status = vendor_reposnse.get('status')
        tracker = sms_models.SMSTracker.objects.get(id=tracker_id)
        if status == 'failure':
            errors = vendor_reposnse.get('errors', None)
            tracker.vendor_error = errors[0].get('message') if errors else ''
            tracker.save()
            return False, errors, tracker_id
        else:
            tracker.batch_id = vendor_reposnse.get('batch_id')
            tracker.vendor_response = self.alter_vendor_response(vendor_reposnse.get('messages'))
            warnings = vendor_reposnse.get('warnings', None)
            tracker.vendor_warning = warnings[0].get('message') if warnings else ''
            tracker.vendor_reponse_status = True
            tracker.save()
            return True, status, tracker_id

    def alter_vendor_response(self, vendor_reposnse):
        altered_vendor_response = {}
        for row in vendor_reposnse:
            altered_vendor_response[row.get('id')] = row.get('recipient')
        return altered_vendor_response

    def get_members(self, serializer):
        serializer_data = serializer.validated_data
        students_list = serializer_data.get('students', [])
        classes_list = serializer_data.get('classes', [])
        class_groups_list = serializer_data.get('class_groups', [])
        sections_list = serializer_data.get('sections', [])
        employees_list = serializer_data.get('employees', [])
        employee_groups_list = serializer_data.get('employee_groups', [])
    
        students = student_models.Profile.objects.values_list('id').filter(
                        Q(id__in=students_list) |
                        Q(class_name__in=classes_list) |
                        Q(class_group__in=class_groups_list) |
                        Q(section__in=sections_list)
                    )
        
        members_as_student = list(map(lambda x:x[0], students))

        
        employees = employee_models.EmployeeDetails.objects.values_list('id').filter(
                Q(id__in=employees_list) |
                Q(department__in=employee_groups_list)
            )
        members_as_employee = list(map(lambda x:x[0], students))
        return members_as_student, members_as_employee

    def get_members_dict(self, student_members, employee_members):
        members_dict = {}
        members_dict['student_members'] = student_members
        members_dict['employee_members'] = employee_members
        group_count = len(student_members) + len(employee_members)
        members_dict['count'] = group_count
        return members_dict

    def get_response(self, send_status, sms_response, tracker_id):
        response = {}
        if not sms_response:
            response['exception'] = 'APIException'
            response['detail'] = "SMS vendor service not reachable"
        if not send_status:
            response['exception'] = 'APIException'
            response['detail'] = sms_response[0].get('message', None)
        else:
            response['id'] = tracker_id
        return response


class SmsGenericMixinViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
                                pass


# class TemplateViewSet(SmsGenericMixinViewSet):
#     queryset = sms_models.Template.objects.all()
#     serializer_class = sms_serializers.TemplateSerializer
#     http_method_names = ['get']

#     def get_serializer_class(self):
#         if self.action == 'create' or self.action == 'update':
#             return sms_serializers.CreateOrUpdateTemplateSerializer
#         return super(TemplateViewSet, self).get_serializer_class()

#     def perform_create(self, serializer):
#         user = self.request.user.id
#         serializer.save(created_by=user, updated_by=user)

#     def update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return super().update(request, *args, **kwargs)


class TemplateViewSet(APIView, TextLocalServices):
    permission_classes = [IsAuthenticated, HasOrganizationAPIKey]

    def get(self, request):
        templates = {}
        # template_id = self.request.query_params.get('templateId', None)
        if request.user.has_perm('sendsms.add_smstracker'):    
            template_api_response = self.get_templates()
            if template_api_response.get('status') == 'success':
                templates = template_api_response.get('templates')
        return response.Response(templates, status=status.HTTP_200_OK)


class SMSViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet, BaseSmsService):

    queryset = sms_models.SMSTracker.objects.all()
    serializer_class = sms_serializers.SendSmsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_status, sms_response, tracker_id = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response(send_status, sms_response, tracker_id)
        return response.Response(data, status=status.HTTP_200_OK, headers=headers)


class SendSMSViewSet(SMSViewSet):
    serializer_class = sms_serializers.SendSmsSerializer

    def perform_create(self, serializer):
        serializer_data = serializer.validated_data
        template = serializer_data.get('message_content', None)
        recipients_source = {}
        recipients_source['student_field_data'] = serializer_data.get('student_id', None)
        recipients_source['class_field_data'] = serializer_data.get('class_id', None)
        recipients_source['class_group_field_data'] = serializer_data.get('class_group', None)
        recipients_source['section_field_data'] = serializer_data.get('section', None)
        recipients_source['addtional_numbers_field_data'] = serializer_data.get('addtional_numbers', [])

        client_request_data, recipients = self.get_client_request_data(recipients_source)
        reference_number = master_services.get_timestamp()
        tracker = serializer.save(
            client_request=client_request_data,
            created_by=self.request.user.id,
            reference_number=reference_number
        )
        return self.get_sms_service(tracker.id, recipients, template)


class SendGroupSMSViewSet(SMSViewSet):
    serializer_class = sms_serializers.GroupSmsSerializer

    def perform_create(self, serializer):
        serializer_data = serializer.validated_data
        template = serializer_data.get('message_content', None)
        group = serializer_data.get('group', None)
        recipients_source = {}
        recipients_source['student_field_data'] = ast.literal_eval(group.students)
        recipients_source['class_field_data'] = ast.literal_eval(group.classes)
        recipients_source['class_group_field_data'] = ast.literal_eval(group.class_groups)
        recipients_source['section_field_data'] = ast.literal_eval(group.sections)
        recipients_source['employee_field_data'] = ast.literal_eval(group.employees)
        recipients_source['employee_group_field_data'] = ast.literal_eval(group.employee_groups)
        
        client_request_data, recipients = self.get_client_request_data(recipients_source)
        reference_number = master_services.get_timestamp()
        tracker = serializer.save(
            client_request=client_request_data,
            created_by=self.request.user.id,
            reference_number=reference_number
        )
        return self.get_sms_service(tracker.id, recipients, template)


class SmsReportViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = sms_models.SMSTracker.objects.all()
    serializer_class = sms_serializers.SmsReportSerializer
    http_method_names = ['get']


class SmsDetailReportViewSet(mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = sms_models.SMSTracker.objects.all()
    serializer_class = sms_serializers.SmsDetailReportSerializer
    http_method_names = ['get']


class GroupViewSet(SmsGenericMixinViewSet, BaseSmsService):
    queryset = sms_models.Group.objects.all()
    serializer_class = sms_serializers.GroupSerializer
    http_method_names = ['get', 'post', 'put']

    def get_serializer_class(self):
        if (self.action == 'create' or self.action == 'update'):
            return sms_serializers.GroupCreateOrUpdateSerializer
        return super(GroupViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        student_members, employee_members = self.get_members(serializer)
        members_dict = self.get_members_dict(student_members, employee_members)
        serializer.save(
            members=members_dict,
            count=members_dict.get('count', None),
            created_by=self.request.user.id,
            updated_by=self.request.user.id
        )

    def perform_update(self, serializer):
        student_members, employee_members = self.get_members(serializer)
        members_dict = self.get_members_dict(student_members, employee_members)
        serializer.save(
            members=members_dict,
            count=members_dict.get('count', None),
            updated_by=self.request.user.id
        )
        serializer.save()
