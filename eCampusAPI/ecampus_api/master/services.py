from datetime import date, datetime
import urllib.request
import urllib.parse
from django.conf import settings
from ecampus_api.settings import local 
import secrets
import hashlib
import time
from master.models import Profile, Repo, RepoClass, ClassName, AcademicYear
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist
from fee import models as fee_models
from master import serializers as master_serializer
from typing import List, Dict

def send_sms(number, message):
    message = message
    data = urllib.parse.urlencode({'apikey': local.SMS_API_KEY, 'senderid': local.SMS_SENDER_ID , 'number': number, 'message': message})
    data = data.encode('utf-8')
    request = ("http://msg.mtalkz.com/V2/http-api.php?")
    smsRes =  urllib.request.urlopen(request, data)
    response = smsRes.read()
    return (response)
    # return True

def get_academic_years() -> Dict[str, Dict[date, date]]:
    academic_years = {}
    
    '''
    function which helps you to get a running and upcoming 
    year from the profile object (instituion details will be store in 
    the profile object)
    return type is dict which contains running and upcoming year as key and 
    value for the key is again a dictionary which contains start and end as key and date as values.
    '''
    
    try:
        academic = Profile.objects.values('id', 'running_academic_start', 'running_academic_end', 'upcoming_academic_start', 'upcoming_academic_end')[0]
        academic_years['running'] = {'start':academic.get('running_academic_start', None), 'end': academic.get('running_academic_end', None)}
        academic_years['upcoming'] = {'start':academic.get('upcoming_academic_start', None), 'end': academic.get('upcoming_academic_end', None)}
    except:
        academic_years['running'] = {'start': None,'end': None}
        academic_years['upcoming'] = {'start': None,'end': None}
    return academic_years

def get_academic_years_key_value(type_of_year) -> List[str]:
    '''
    function which calls the get_academic_years(), and gets the running and
    upcoming years and converts in the form of year_year (2022_2023)
    which is basically startyear_endyear 
    '''
    try:
        start_year, end_year = get_academic_years()[type_of_year]['start'].year, get_academic_years()[type_of_year]['end'].year
        key, value = str(start_year) +'_'+ str(end_year), str(start_year) +' - '+ str(end_year)
    except:
        key, value = None, None
    return [key, value]


def get_reference_numer(*argv, **kwargs):
    ad_object, aid, year = kwargs.get('ad_object', None), kwargs.get('aid', None), kwargs.get('academic_year', None)
    applications = ad_object.objects.select_for_update().filter(~Q(id=aid), academic_year=year, reference_number__isnull=False)
    refrence_number =  year[2:4] + year[-2:] + "{:02d}".format(len(applications) + 1)
    return refrence_number

def get_timestamp():
    return str(time.time()).replace(".","")

def unique_token():
    salt = secrets.token_hex(8)   + get_timestamp()
    unique_token = hashlib.sha256(salt.encode('utf-8')).hexdigest()
    return unique_token

def update_repo(data):
    run_start = data.get('running_academic_start', None)
    run_end = data.get('running_academic_end', None)
    up_start = data.get('upcoming_academic_start', None)
    up_end = data.get('upcoming_academic_end', None)
    accounting_start = data.get('financial_start', None)
    accounting_end = data.get('financial_end', None)
    try:
        run_academic_year = run_start[0:4] + "_" + run_end[0:4]
        upcoming_academic_year = up_start[0:4] + "_" + up_end[0:4]
        if not Repo.objects.filter(admission_academic_year=run_academic_year).exists():
            run_repo = Repo.objects.create(admission_academic_year=run_academic_year)
            run_repo.save()
        if not Repo.objects.filter(academic_year=upcoming_academic_year).exists():
            up_repo = Repo.objects.create(academic_year=upcoming_academic_year)
            up_repo.save()
        if not RepoClass.objects.filter(admission_academic_year=run_academic_year).exists():
            classes = ClassName.objects.all()
            for cl in classes:
                class_repo = RepoClass.objects.create(admission_academic_year=run_academic_year, cid=cl)
                class_repo.save()
        if not AcademicYear.objects.filter(academic_year=run_academic_year).exists():
            up_academic_repo = AcademicYear.objects.create(
                academic_year=run_academic_year,
                start=run_start,
                end=run_end)
            up_academic_repo.save()
        else:
            AcademicYear.objects.filter(
                academic_year=run_academic_year).update(start=run_start, end=run_end)
        for category in fee_models.FeeCategory.objects.all():
            if not fee_models.FeeBillRepo.objects.filter(fee_category=category.id, accounting_start__gte=accounting_start, accounting_end__lte=accounting_end).exists():
                fee_models.FeeBillRepo.objects.create(fee_category=category, accounting_start=accounting_start, accounting_end=accounting_end)
    except Exception as e:
        return False

def get_institution_prefix():
    institution = Profile.objects.values('institution_name')[0]
    institution_name = institution.get('institution_name').split(" ")
    size = len(institution_name)
    if size == 1:
        institution_prefix = institution_name[0][0:3]
    elif  size == 2:
        institution_prefix = institution_name[0][0] + institution_name[1][0]
    else:
        institution_prefix = institution_name[0][0] + institution_name[1][0] + institution_name[2][0]
    return institution_prefix.upper()

def get_related(instanceObject, primary_field_name, *args):
    print(args)
    if instanceObject:
        related_dict = [{"id":instanceObject.id, "name":getattr(instanceObject, primary_field_name)}] if hasattr(instanceObject, primary_field_name) else None
        if args:
            for arg in args:
                for extra_field in arg:
                    related_dict[0][extra_field] = getattr(instanceObject, extra_field) if hasattr(instanceObject, extra_field) else None
        return related_dict
    return None

def get_related_feecategory(instanceObject, primary_field_name, second_field_name, *args):
    print(args)
    if instanceObject:
        related_dict = [{"id":instanceObject.id, "name":getattr(instanceObject, primary_field_name),"company_name":getattr(instanceObject, second_field_name)}] if hasattr(instanceObject, primary_field_name) else None
        if args:
            for arg in args:
                if not isinstance(arg,str):
                    for extra_field in arg:
                        related_dict[0][extra_field] = getattr(instanceObject, extra_field) if hasattr(instanceObject, extra_field) else None
                else:
                    related_dict[0][arg] = getattr(instanceObject, arg) if hasattr(instanceObject, arg) else None
        return related_dict
    return None
    
def get_all_academic_years():
    all_academic_years = AcademicYear.objects.values('id', 'academic_year', 'start', 'end')
    return all_academic_years

def check_academic_year(year):
    if AcademicYear.objects.filter(academic_year=year).exists():
        return True
    else:
        return False
    
def get_academic_year_string(start, end):
    
    '''
    this function get the starting and ending 
    academic year date and returns 
    academic year string
    '''
    start_date = datetime.strptime(start,"%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    return str(start_date.year) + "_" + str(end_date.year)
    
def get_institution_all_academic_year():
    response_data = AcademicYear.objects.all().order_by('-academic_year')
    serializer = master_serializer.AcademicYearSerializer(response_data, many=True)
    return serializer.data