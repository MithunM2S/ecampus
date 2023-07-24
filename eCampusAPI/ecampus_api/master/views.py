from django.shortcuts import render, get_object_or_404
from master import models as master_models
from rest_framework import generics
from rest_framework import viewsets, mixins
from master import serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api_authentication import permissions as api_permissions
from employee.permissions import EmployeeHasPermission, EmployeeHasSpecificPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from api_authentication.permissions import HasOrganizationAPIKey
from rest_framework.permissions import AllowAny
from master.services import get_academic_years, update_repo, get_all_academic_years, get_academic_year_string, get_institution_all_academic_year
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from django.db import connection


class MasterGenericMixinViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
                                pass

class AcademicYear(APIView):
    permission_classes = [AllowAny, HasOrganizationAPIKey]
    serializer_class = serializers.AcademicYearSerializer

    def get(self, request):
        return Response(get_academic_years())
    
    def post(self, request):

        #adding academic_year string as we get only start and end date
        try:
            request.data['academic_year'] = get_academic_year_string(request.data['start'], request.data['end'])
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(get_institution_all_academic_year())
            else:
                return Response(serializer.errors)
        except:
            return Response({
                "data" : "Format for start or end date properly not recieved"
            })
    
    def delete(self, request):
        try:
            academic_year = get_object_or_404(master_models.AcademicYear, id=request.data['id'])
            if academic_year:
                academic_year.delete()
                return Response(get_institution_all_academic_year())
        except:
            return Response({
                'data' : 'academic year doesn\'t exist'
            })
            
        
    def put(self, request):
        try:
            data = request.data
            academic_year = get_object_or_404(master_models.AcademicYear, id=request.data['id'])
            if academic_year:
                request.data['academic_year'] = get_academic_year_string(request.data['start'], request.data['end'])
                serializer = self.serializer_class(academic_year, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(get_institution_all_academic_year())
                else:
                    return Response(serializer.errors)
        except:
            return Response({'data' : 'the academic year doesn\'t exist'})
        
        

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = master_models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ProfileCreateSerializer
        if self.action == 'update':
            return serializers.ProfileUpdateSerializer
        if self.action == 'retrieve':
            return serializers.ProfileDetailSerializer
        if self.action == 'list':
            return serializers.ProfileDetailSerializer
        return super(ProfileViewSet, self).get_serializer_class()

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            self.permission_classes = [AllowAny, HasOrganizationAPIKey]
        return super().get_permissions()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user  = self.request.user.id
        else:
            user = 0
        serializer.save(created_by=user)
        update_repo(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
        update_repo(serializer.data)

class ClassGroupViewset(viewsets.ModelViewSet):
    queryset = master_models.ClassGroup.objects.all()
    serializer_class = serializers.ClassGroupSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ClassGroupCreateUpdateSerializer
        if self.action == 'update':
            return serializers.ClassGroupCreateUpdateSerializer
        if self.action == 'retrieve':
            return serializers.ClassGroupDetailSerializer
        if self.action == 'list':
            return serializers.ClassGroupDetailSerializer
        return super(ClassGroupViewset, self).get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user = self.request.user.id
        else:
            user = 0
        serializer.save(created_by=user)

class ClassNameViewset(viewsets.ModelViewSet):
    queryset = master_models.ClassName.objects.all()
    serializer_class = serializers.ClassNameSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ClassNameCreateSerializer
        if self.action == 'update':
            return serializers.ClassNameUpdateSerializer
        if self.action == 'retrieve':
            return serializers.ClassNameDetailSerializer
        if self.action == 'list':
            return serializers.ClassNameDetailSerializer
        return super(ClassNameViewset, self).get_serializer_class()

    def perform_create(self, serializer):
        class_name = master_models.ClassName.objects.all()
        class_code = "{:02d}".format(len(class_name) + 1)
        serializer.save(created_by=self.request.user.id, class_code=class_code)

class SectionViewset(viewsets.ModelViewSet):
    queryset = master_models.Section.objects.all()
    serializer_class = serializers.SectionSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.SectionCreateSerializer
        if self.action == 'update':
            return serializers.SectionUpdateSerializer
        if self.action == 'retrieve':
            return serializers.SectionDetailSerializer
        if self.action == 'list':
            return serializers.SectionDetailSerializer
        return super(SectionViewset, self).get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user = self.request.user.id
        else:
            user = 0
        serializer.save(created_by=user)

class CategoryViewset(viewsets.ModelViewSet):
    queryset = master_models.CasteCategory.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CategoryCreateSerializer
        if self.action == 'update':
            return serializers.CategoryUpdateSerializer
        if self.action == 'retrieve':
            return serializers.CategoryDetailSerializer
        if self.action == 'list':
            return serializers.CategoryDetailSerializer
        return super(SectionViewset, self).get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user = self.request.user.id
        else:
            user = 0
        serializer.save(created_by=user)

class CasteViewset(viewsets.ModelViewSet):
    queryset = master_models.Caste.objects.all()
    serializer_class = serializers.CasteSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CasteCreateSerializer
        if self.action == 'update':
            return serializers.CasteUpdateSerializer
        if self.action == 'retrieve':
            return serializers.CasteDetailSerializer
        if self.action == 'list':
            return serializers.CasteDetailSerializer
        return super(SectionViewset, self).get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user = self.request.user.id
        else:
            user = 0
        serializer.save(created_by=user)

class AnonymousUserClasses(APIView):
    permission_classes = [AllowAny, HasOrganizationAPIKey]

    def get(self,request):
        queryset = master_models.ClassName.objects.values('id','class_name')
        return Response(queryset)


class ClassPredictor(APIView):
    permission_classes = [AllowAny, HasOrganizationAPIKey]

    def get(self,request,input_age):
        queryset = master_models.ClassName.objects.values('id').filter(from_age__lte = input_age,to_age__gte = input_age)
        if queryset:
            return Response(queryset[0])
        else:
            return Response([{'id':1}]) #for invalid age

class SubjectViewSet(MasterGenericMixinViewSet):
    queryset = master_models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            self.serializer_class = serializers.CreateOrUpdateSubjectSerializer
            return self.serializer_class
        return super().get_serializer_class()

class GenderViewSet(MasterGenericMixinViewSet):
    queryset = master_models.Gender.objects.all()
    serializer_class = serializers.GenderSerializer

class QuotaViewSet(MasterGenericMixinViewSet):
    queryset = master_models.Quota.objects.all()
    serializer_class = serializers.QuotaSerializer

class ReligionViewSet(MasterGenericMixinViewSet):
    queryset = master_models.Religion.objects.all()
    serializer_class = serializers.ReligionSerializer

class MotherTongueViewSet(MasterGenericMixinViewSet):
    queryset = master_models.MotherTongue.objects.all()
    serializer_class = serializers.MotherTongueSerializer
    # http_method_names = ['get', 'post']

class ListAcademicYear(APIView):
    permission_classes = [HasOrganizationAPIKey, IsAuthenticated]

    def get(self, request):
        return Response(get_institution_all_academic_year())
    


@api_view(['POST'])
@permission_classes([AllowAny])
def auto_add_academic_year(request):
    
    '''
    This is a function which adds academic years automatically by
    taking how many years you want to add automatically as input
    '''
    
    if request.method == 'POST':
        data = request.data
        number_of_years = int(data['number_of_years'])
        try:
            existing_last_academic_year = master_models.AcademicYear.objects.order_by('start')[0]
            existing_last_academic_year_start = existing_last_academic_year.start
            existing_last_academic_year_end = existing_last_academic_year.end
            print(existing_last_academic_year_start, existing_last_academic_year_end)
            for i in range(1, number_of_years + 1):
                start = existing_last_academic_year_start.replace(year = existing_last_academic_year_start.year - i)
                end = existing_last_academic_year_end.replace(year = existing_last_academic_year_end.year - i)
                academic_year = str(start.year) + "_" + str(end.year)
                master_models.AcademicYear.objects.create(academic_year=academic_year, start=start,end=end)
            return Response(get_institution_all_academic_year())
        except master_models.AcademicYear.DoesNotExist:
            return {'message' : 'there\'s no existing year please add atleast one academci year to auto add'}
        except:
            return {'message' : 'Internal server error'}

class StudentRegisterFieldsViewSet(MasterGenericMixinViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put']

    def create_def(*args,**kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO master_studentregisterfields VALUES (1,'student-aadhar-number',True);
                    """
                )
        except Exception as e:
            print(e)

    queryset = master_models.StudentRegisterFields.objects.all()
    if not queryset:
        create_def()
    serializer_class = serializers.StudentRegisterFieldsSerializer
        