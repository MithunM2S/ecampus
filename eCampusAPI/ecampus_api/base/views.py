from rest_framework import response, status
from django.shortcuts import get_list_or_404, get_object_or_404
from django.views import View
import pandas as pa
from preadmission.models import Application
from master import services, models as master_models
from student import models as student_models
from django.db import transaction
import datetime

class DestroyWithPayloadMixin(object):

     def destroy(self, *args, **kwargs):
         serializer = self.get_serializer(self.get_object())
         super().destroy(*args, **kwargs)
         return response.Response(serializer.data, status=status.HTTP_200_OK)

class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.

    Source: https://www.django-rest-framework.org/api-guide/generic-views/#creating-custom-mixins
    Modified to not error out for not providing all fields in the url.
    """

    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field):  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj

class ImportStudents(View):

    def get(self, request):
        data = pa.read_excel (r'/media/ajith/AK/Projects/Docs/eCampus/Siddaganga.xlsx').fillna('')
        application_data, profile_data, parent_data = {}, {}, {}
        for row in data.itertuples():
            sname = row.StudentName if row.StudentName else 'Student'
            if str(sname):
                admission_academic_year = '2020_2021'
                ref_repo = master_models.Repo.objects.get(academic_year=admission_academic_year)
                new_reference_number = ref_repo.reference_number + 1
                ref_repo.reference_number = new_reference_number
                ref_repo.save()
                class_group_id = master_models.ClassGroup.objects.get(id=int(row.ClassGroupID))
                class_id = master_models.ClassName.objects.get(id=int(row.ClassID))
                section_id = master_models.Section.objects.get(id=int(row.SectionID))
                gender = master_models.Gender.objects.get(id=int(row.GenderID))
                quota = master_models.Quota.objects.get(id=int(row.QuotaID))
                mothertongue = master_models.MotherTongue.objects.get(id=int(row.MotherTongueID))
                # dd = datetime_object = datetime.datetime.strptime(row.DateofBirth, "%Y-%m-%d")
                print(row.DateOfBirth)
                dob = pa.to_datetime(row.DateOfBirth, format='%d/%m/%Y').strftime("%Y-%m-%d") if row.DateOfBirth else '2021-12-12'
                religion = master_models.Religion.objects.get(id=int(row.ReligionID))
                mother_tongue_id = master_models.MotherTongue.objects.get(id=int(row.MotherTongueID))
                # address = "None" 
                address = str(row.Address1) + str(row.Address2) + str(row.Address3) + str(row.Address4)
                father_mobile = row.MobileNum
                father_name = row.FatherName
                mother_name = row.MotherName
                # row.MotherName
                mother_mobile = None

                reference_number =  admission_academic_year[2:4] + admission_academic_year[-2:] + "{:02d}".format(new_reference_number)
                student_name = str(sname).strip()
                
                application_data['student_name'] = student_name
                application_data['dob'] = dob
                application_data['class_name'] = class_id
                application_data['father_name'] = father_name
                application_data['mother_name'] = mother_name
                application_data['is_verified'] = 1
                application_data['created_by'] = 0
                application_data['is_applied'] = 1
                application_data['reference_number'] = reference_number
                application_data['gender'] = gender
                application_data['application_token'] = services.unique_token()
                application_data['is_docs_verified'] = 1
                application_data['academic_year'] = admission_academic_year
                application_data['existing_parent'] = 'no'
                application_data['primary_contact_person'] = 'father'
                application = Application.objects.create(**application_data)
                
                if (application):
                    admit_repo = master_models.Repo.objects.get(admission_academic_year=admission_academic_year)
                    repo_new_admission_number = admit_repo.admission_number + 1
                    admit_repo.admission_number = repo_new_admission_number
                    admit_repo.save()
                    # class_obj = master_models.RepoClass.objects.get(admission_academic_year=admission_academic_year, cid=class_id.id)
                    # class_code = class_id.class_code
                    # student_id = (class_obj.max_strength - class_obj.available_strength) + 1
                    # class_obj.available_strength = class_obj.available_strength - 1
                    # class_obj.save()
                    admission_number =  admission_academic_year[2:4] + admission_academic_year[-2:] + "{:02d}".format(repo_new_admission_number)
                    # new_student_id = services.get_institution_prefix() + str(admission_academic_year[2:4]) + str(class_code) + str("{:02d}".format(student_id))
                    # admission_academic_year[0:2]
                    profile_data['application_id'] = application.id
                    profile_data['admission_number'] =  admission_number
                    profile_data['admission_academic_year'] = admission_academic_year
                    profile_data['student_id'] = 1000 + student_models.Profile.objects.all().count() + 1
                    profile_data['first_name'] = student_name
                    # profile_data['last_name'] = "student_name"
                    profile_data['gender'] = gender
                    profile_data['dob'] = dob
                    profile_data['place_of_brith'] = None
                    profile_data['sats_number'] = application.id
                    profile_data['combination'] = 'state'
                    profile_data['quota'] =  quota
                    profile_data['mother_tongue'] =  mothertongue
                    profile_data['nationality'] = 'Indian'
                    profile_data['religion'] = religion
                    profile_data['primary_contact'] = 'father'
                    profile_data['current_address'] = address
                    profile_data['created_by'] = 0
                    # profile_data['caste_id'] = 1
                    # profile_data['caste_category_id'] = 1
                    profile_data['class_name'] = class_id
                    profile_data['section'] = section_id
                    profile = student_models.Profile.objects.create(**profile_data)
                    if profile:
                        parent_data['student'] = profile
                        parent_data['father_name'] = father_name
                        parent_data['mother_name'] = mother_name
                        parent_details = student_models.ParentDetails.objects.create(**parent_data)
                    student_history = student_models.History.objects.create(student=profile, to_class=class_id.id, to_academic_year=admission_academic_year)
