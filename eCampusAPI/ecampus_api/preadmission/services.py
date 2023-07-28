from master import services
from django.db.models import Q, Count, F, Case, When, IntegerField, Sum
from django.db.models.functions import Cast
from master.models import Repo, ClassGroup, ClassName, Section, GroupConcat
from student.models import Profile
from preadmission.models import Application

class PreadmissionCountService(object):

    # init method or constructor
    def __init__(self, academic_year=None):
        if academic_year:
            self.filter_acdemic_year = academic_year
        else:
            self.filter_acdemic_year = services.get_academic_years_key_value('running')[0]
        self.queryset = Application.objects.filter(academic_year=self.filter_acdemic_year)
    
    # Get total application count
    # def get_total_application_count(self):
    #     total_application_count = self.queryset.count()
    #     return total_application_count

    # Get verified application count
    # def get_verified_application_count(self,):
    #     verified_application_count = self.queryset.filter(is_verified=True).count()
    #     return verified_application_count

    # Get pending verification count
    # def get_pending_verification_count(self,):
    #     pending_verification_count = self.queryset.filter(is_verified=False).count()
    #     return pending_verification_count

    # Get submitted application count
    # def get_submitted_application_count(self,):
    #     submitted_application_count = self.queryset.filter(is_docs_verified=False, is_applied=True).count()
    #     return submitted_application_count

    # Get pendig docs verification pending count
    # def get_pending_docs_verification_count(self,):
    #     pending_docs_verification_count = self.queryset.filter(is_docs_verified=False, is_applied=True).count()
    #     return pending_docs_verification_count
    
    # Get docs verified count
    # def get_docs_verified_count(self,):
    #     docs_verifed_count = self.queryset.filter(is_docs_verified=True, is_applied=True).count()
    #     return docs_verifed_count

    # Get Admitted student count
    # def get_admitted_student_count(self,):
    #     admitted_student_count = self.queryset.filter(is_docs_verified=True, is_applied=True, is_admitted=True).count()
    #     # admitted_student_count = Profile.objects.filter(application_id__in=application_student).count()
    #     return admitted_student_count

    # Get Class group wise count 
    def get_class_group_wise_student_count(self,):
        class_groupwise_student_count = []
        # ClassName.objects.select_related('class_group').values('class_group').annotate(count=Count('class_group')).annotate(class_ids=GroupConcat('id'))
        # class_group_classes = ClassName.objects.select_related('class_group').values('class_group').annotate(count=Count('class_group')).annotate(class_ids=GroupConcat('id'))
        queryset = self.queryset.filter(is_docs_verified=True, is_applied=True)
        for classGroupObject in ClassGroup.objects.all():
            count = queryset.filter(class_name__in=ClassName.objects.filter(class_group=classGroupObject.id)).count()
            class_data = []
            for classObject in ClassName.objects.filter(class_group=classGroupObject.id):
                class_data.append({"id": classObject.id, "name": classObject.class_name, "count": queryset.filter(class_name=classObject.id).count()})
            class_groupwise_student_count.append({"id": classGroupObject.id, "name":classGroupObject.class_group, "count":count, "class": class_data})
        return class_groupwise_student_count

    # Get Class wise count 
    def get_class_wise_student_count(self,):
        class_wise_student_count = []
        for cname in ClassName.objects.select_related('class_group').all():
            count = self.queryset.filter(is_docs_verified=True, is_applied=True, class_name=cname.id).count()
            data = {
                "id":cname.id,
                "class_name":cname.class_name,
                "count": count,
                "class_group": {
                    "id": cname.class_group.id,
                    "name": cname.class_group.class_group,
                }
            }
            class_wise_student_count.append(data)
        return class_wise_student_count

    # Get online enquiry count
    def get_online_enquiry_count(self,):
        online_enquiry_count = self.queryset.filter(mode=True).count()
        return online_enquiry_count

    # Get offline enquiry count
    def get_offline_enquiry_count(self,):
        offline_enquiry_count = self.queryset.filter(mode=False).count()
        return offline_enquiry_count

    def get_card_count(self, card_name, mode):
        queryset = self.queryset.values('academic_year').order_by().annotate(
            total=Count('id'),
            verified=Count('is_verified', filter=Q(is_verified=True)),
            unverified=Count('is_verified', filter=Q(is_verified=False)),
            doc_submitted=Count('is_applied', filter=Q(is_applied=True)),
            doc_verified=Count('is_docs_verified', filter=Q(is_docs_verified=True)),
            doc_unverified=Count('is_docs_verified', filter=Q(is_applied=True) & Q(is_docs_verified=False)),
            admitted=Count('is_admitted', filter=Q(is_admitted=True)),
            not_admitted=Count('is_admitted', filter=Q(is_admitted=False)),
            online_count=Count('mode', filter=Q(mode=True)),
            offline_count=Count('mode', filter=Q(mode=False)), #mode is True if it's applied online
            verified_online_count=Count('mode', filter=Q(mode=True) & Q(is_verified=True)),
            verified_offline_count=Count('mode', filter=Q(mode=False) & Q(is_verified=True)),
            unverified_online_count=Count('mode', filter=Q(mode=True) & Q(is_verified=False)),
            unverified_offline_count=Count('mode', filter=Q(mode=False) & Q(is_verified=False)),
            doc_submitted_online_count=Count('mode', filter=Q(mode=True) & Q(is_applied=True)),
            doc_submitted_offline_count=Count('mode', filter=Q(mode=False) & Q(is_applied=True)),
            doc_verified_online_count=Count('mode', filter=Q(mode=True) & Q(is_docs_verified=True)),
            doc_verified_offline_count=Count('mode', filter=Q(mode=False) & Q(is_docs_verified=True)),
            doc_unverified_online_count=Count('mode', filter=Q(mode=True) & Q(is_applied=True) & Q(is_docs_verified=False)),
            doc_unverified_offline_count=Count('mode', filter=Q(mode=False) & Q(is_applied=True) & Q(is_docs_verified=False)),
            admitted_online_count=Count('mode', filter=Q(mode=True) & Q(is_admitted=True)),
            admitted_offline_count=Count('mode', filter=Q(mode=False) & Q(is_admitted=True)),
            not_admitted_online_count=Count('mode', filter=Q(mode=True) & Q(is_admitted=False)),
            not_admitted_offline_count=Count('mode', filter=Q(mode=False) & Q(is_admitted=False)),
        )
        if queryset:
            del queryset[0]['academic_year']
        return queryset
