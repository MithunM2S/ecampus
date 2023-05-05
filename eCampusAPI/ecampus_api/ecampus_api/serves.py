
from student.models import Document, Profile
from preadmission.models import Application
from master import models as master_models
from student import models as student_models
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.conf.urls.static import static
from django.views.static import serve
import os

faield_response = []
faield_response.append({'status':404, "message": "File not found"})

def protected_document_serve(request, docid, path, document_root=None):
    try:
        app_obj = Application.objects.get(application_token=request.GET.get('token'), reference_number=request.GET.get('ref'))
        doc_obj = student_models.Document.objects.get(id=app_obj.docs_id)
        correct_image_url = getattr(doc_obj, request.GET.get('target')).url.replace("/media/", "")
        full_path = os.path.join('uploads/'+ request.GET.get('dir') + '/', str(doc_obj.id)) + "/" + path
        if correct_image_url == full_path:
            return serve(request, full_path, document_root)
        return JsonResponse(faield_response, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(faield_response, safe=False)

def protected_student_picture_serve(request, studentId, path, document_root=None):
    try:
        student_obj = student_models.Profile.objects.get(student_id=studentId)
        correct_profil_pic_url = getattr(student_obj, 'picture').url.replace("/media/", "")
        full_path = os.path.join('uploads/student-profile' + '/', str(student_obj.student_id)) + "/" + path
        if correct_profil_pic_url == full_path and request.user.is_authenticated:
            return serve(request, full_path, document_root)
        return JsonResponse(faield_response, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(faield_response, safe=False)

def protected_institution_logo_serve(request, profileId, path, document_root=None):
    try:
        master_profile_obj = master_models.Profile.objects.get(id=profileId)
        correct_logo_url = getattr(master_profile_obj, 'logo').url.replace("/media/", "")
        full_path = os.path.join('uploads/institution-profile' + '/', str(master_profile_obj.id)) + "/" + path
        if correct_logo_url == full_path and request.user.is_authenticated:
            return serve(request, full_path, document_root)
        return JsonResponse(faield_response, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(faield_response, safe=False)

def fee_report_file_serve(request, path, document_root=None):
    try:
        full_path = "files/fee/" + path
        if request.user.is_authenticated and request.user.has_perm('fee.can_view_fee_collection'):
            return serve(request, full_path, document_root)
        return JsonResponse(faield_response, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(faield_response, safe=False)
