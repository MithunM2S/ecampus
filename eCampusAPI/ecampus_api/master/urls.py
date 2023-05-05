from django.urls import path, include, re_path
from master import views as master_views 
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'subjects', master_views.SubjectViewSet)
router.register(r'gender', master_views.GenderViewSet)
router.register(r'quota', master_views.QuotaViewSet)
router.register(r'religion', master_views.ReligionViewSet)
router.register(r'mother-tongue', master_views.MotherTongueViewSet)

urlpatterns = [
    path('academic-years/',master_views.AcademicYear.as_view(), name='current_academic_year'),
    path('list-academic-years/',master_views.ListAcademicYear.as_view(), name='list_academic_year'),
    path('profile/list/', master_views.ProfileViewSet.as_view({'get':'list'}), name='list_profile'),
    path('profile/detail/<pk>/', master_views.ProfileViewSet.as_view({'get':'retrieve'}), name='profile'),
    path('profile/create/', master_views.ProfileViewSet.as_view({'post':'create'}), name='create_profile'),
    path('profile/update/<pk>/', master_views.ProfileViewSet.as_view({'put':'update'}), name='update_profile'),
    # path('profile/delete/<pk>/', master_views.ProfileViewSet.as_view({'delete':'destroy'}), name='delete_profile'),
    path('class/group/create/', master_views.ClassGroupViewset.as_view({'post':'create'}), name='create_class_group'),
    path('class/group/list/', master_views.ClassGroupViewset.as_view({'get':'list'}), name='list_class_group'),
    path('class/group/detail/<pk>/', master_views.ClassGroupViewset.as_view({'get':'retrieve'}), name='detail_class_group'),
    path('class/group/update/<pk>/', master_views.ClassGroupViewset.as_view({'put':'update'}), name='update_class_group'),
    path('class/group/delete/<pk>/', master_views.ClassGroupViewset.as_view({'delete':'destroy'}), name='delete_class_group'),
    path('class/name/create/', master_views.ClassNameViewset.as_view({'post':'create'}), name='create_class_name'),
    path('class/name/list/', master_views.ClassNameViewset.as_view({'get':'list'}), name='list_class_name'),
    path('class/name/detail/<pk>/', master_views.ClassNameViewset.as_view({'get':'retrieve'}), name='detail_class_name'),
    path('class/name/update/<pk>/', master_views.ClassNameViewset.as_view({'put':'update'}), name='update_class_name'),
    path('class/name/delete/<pk>/', master_views.ClassNameViewset.as_view({'delete':'destroy'}), name='delete_class_name'),
    path('section/create/', master_views.SectionViewset.as_view({'post': 'create'}), name='create_class_section'),
    path('section/list/', master_views.SectionViewset.as_view({'get': 'list'}), name='list_class_section'),
    path('section/detail/<pk>/', master_views.SectionViewset.as_view({'get': 'retrieve'}), name='detail_class_section'),
    path('section/update/<pk>/', master_views.SectionViewset.as_view({'put': 'update'}), name='update_class_section'),
    path('section/delete/<pk>/', master_views.SectionViewset.as_view({'delete': 'destroy'}), name='delete_class_section'),
    path('caste/category/create/', master_views.CategoryViewset.as_view({'post': 'create'}), name='create_category'),
    path('caste/category/list/', master_views.CategoryViewset.as_view({'get': 'list'}), name='list_category'),
    path('caste/category/detail/<pk>/', master_views.CategoryViewset.as_view({'get': 'retrieve'}), name='detail_category'),
    path('caste/category/update/<pk>/', master_views.CategoryViewset.as_view({'put': 'update'}), name='update_category'),
    path('caste/category/delete/<pk>/', master_views.CategoryViewset.as_view({'delete': 'destroy'}), name='delete_category'),
    path('caste/create/', master_views.CasteViewset.as_view({'post': 'create'}), name='create_caste'),
    path('caste/list/', master_views.CasteViewset.as_view({'get': 'list'}), name='list_caste'),
    path('caste/detail/<pk>/', master_views.CasteViewset.as_view({'get': 'retrieve'}), name='detail_caste'),
    path('caste/update/<pk>/', master_views.CasteViewset.as_view({'put': 'update'}), name='update_caste'),
    path('caste/delete/<pk>/', master_views.CasteViewset.as_view({'delete': 'destroy'}), name='delete_caste'),
    path('classes/anonymous/', master_views.AnonymousUserClasses.as_view(), name='anonymous_list_class_name'),
    path('services/class-for-age/input_age=<input_age>/', master_views.ClassPredictor.as_view(), name='get_class_name_by_age'),
]
urlpatterns += router.urls