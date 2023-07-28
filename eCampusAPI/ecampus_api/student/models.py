from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from master.models import (
                    ClassGroup,
                    ClassName, 
                    Caste, 
                    CasteCategory, 
                    Section, 
                    Gender, 
                    Quota, 
                    Religion, 
                    MotherTongue
                )
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.conf import settings
from django.utils.timezone import now


_UNSAVED_1,  _UNSAVED_2, _UNSAVED_3 = 'unsaved_1', 'unsaved_2', 'unsaved_3'

def get_upload_path(instance, file_name):
    return "uploads/documents/{0}/{1}".format(instance.pk, file_name)

def get_profile_pic_upload_path(instance, file_name):
    return "uploads/student-profile/{0}/{1}".format(instance.student_id, file_name)

class Document(models.Model):
    # student = models.OneToOneField(Profie, on_delete=models.PROTECT, null=True)
    student_photo = models.ImageField('Photo', upload_to=get_upload_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])], null=True)
    birth_certificate = models.ImageField('Photo', upload_to=get_upload_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])], null=True)
    tc = models.ImageField('Photo', upload_to=get_upload_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])], null=True)
    other_document = models.ImageField('Photo', upload_to=get_upload_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])], null=True)
    uploaded_on = models.DateTimeField('Uploaded On', auto_now_add=True)

@receiver(pre_save, sender=Document)
def skip_saving_file(sender, instance, **kwargs):
    if not instance.pk:
        if not hasattr(instance, _UNSAVED_1):
            setattr(instance, _UNSAVED_1, instance.student_photo)
            instance.student_photo = None
        if not hasattr(instance, _UNSAVED_2):
            setattr(instance, _UNSAVED_2, instance.birth_certificate)
            instance.birth_certificate = None
        if not hasattr(instance, _UNSAVED_3):
            setattr(instance, _UNSAVED_3, instance.tc)
            instance.tc = None

@receiver(post_save, sender=Document)
def save_file(sender, instance, created, **kwargs):
        if created:
            if hasattr(instance, _UNSAVED_1):
                instance.student_photo = getattr(instance, _UNSAVED_1)
            if hasattr(instance, _UNSAVED_2):
                instance.birth_certificate = getattr(instance, _UNSAVED_2)
            if hasattr(instance, _UNSAVED_3):
                instance.tc = getattr(instance, _UNSAVED_3)
            instance.save()
            # delete it if you feel uncomfortable...
            instance.__dict__.pop(_UNSAVED_1)
            instance.__dict__.pop(_UNSAVED_2)
            instance.__dict__.pop(_UNSAVED_3)

class Profile(models.Model):
    application_id = models.PositiveIntegerField('Application Id', unique=True)
    admission_number = models.CharField('Admission Number', null=True, unique=True, max_length=25)
    admission_on = models.DateTimeField(auto_now_add=True)
    admission_academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')])
    student_id = models.CharField('Student Id', max_length=15, unique=True, editable=False)
    first_name = models.CharField('First Name', validators=[MinLengthValidator(1), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    last_name = models.CharField('Last Name', validators=[MinLengthValidator(1), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)
    dob = models.DateField('Date of Birth')
    place_of_brith = models.CharField(max_length=35, null=True)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, null=True)
    class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, null=True)
    sats_number = models.CharField('SATS Number', max_length=20, null=True)
    combination = models.CharField('Combination', choices=settings.COMBINATION_CHOICES, max_length=10, default='state', null=True)
    quota = models.ForeignKey(Quota, on_delete=models.PROTECT, null=True)
    student_mobile = models.CharField('Studnet Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True)
    student_email = models.EmailField('Student Email Address', null=True)
    nationality = models.CharField('Nationality', validators=[MinLengthValidator(3)], max_length=10, null=True)
    religion = models.ForeignKey(Religion, on_delete=models.PROTECT, null=True)
    mother_tongue = models.ForeignKey(MotherTongue, on_delete=models.PROTECT, null=True)
    caste = models.ForeignKey(Caste, on_delete=models.PROTECT, null=True)
    caste_category = models.ForeignKey(CasteCategory, on_delete=models.PROTECT, null=True)
    primary_contact = models.CharField(choices=settings.PRIMARY_CONTACT_CHOICE, max_length=10)
    current_address = models.TextField('Current Address')
    permanent_address = models.TextField('Permanent Address', null=True)
    previous_school = models.CharField('Previous School Name', max_length=200, null=True, blank=True)
    document = models.OneToOneField(Document, on_delete=models.PROTECT, null=True)
    picture = models.ImageField('Photo', upload_to=get_profile_pic_upload_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])], null=True)
    created_by = models.IntegerField('Created By', default=0)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField('Is active', default=True)
    student_aadhar_number = models.BigIntegerField(null=True, unique=True)

    class Meta:
        ordering = ['-id']

class ParentDetails(models.Model):
    student = models.OneToOneField(Profile, related_name= 'parent_details', on_delete=models.PROTECT)
    father_name =  models.CharField('Father name', validators=[MinLengthValidator(3), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    father_mobile = models.CharField('Father Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True)
    father_email = models.EmailField('Father Email Address', null=True)
    father_qualification = models.CharField('Father Qualification', max_length=20, null=True)
    father_occupation = models.CharField('Father Occupation', max_length=20, null=True)
    father_annual_income = models.DecimalField('Father Annual Income', max_digits=10, decimal_places=2, null=True)
    father_address = models.TextField('Father Address', null=True)
    mother_name =  models.CharField('Mother name', validators=[MinLengthValidator(3), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    mother_mobile = models.CharField('Mother Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True)
    mother_email = models.EmailField('Mother Email Address', null=True)
    mother_qualification = models.CharField('Mother Qualification', max_length=20, null=True)
    mother_occupation = models.CharField('Mother Occupation', max_length=20, null=True)
    mother_annual_income = models.DecimalField('Mother Annual Income', max_digits=10, decimal_places=2, null=True)
    mother_address = models.TextField('Mother Address', null=True)
    guardian_name =  models.CharField('Guardian name', validators=[RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60, null=True)
    guardian_mobile = models.CharField('Guardian Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True)
    guardian_email = models.EmailField('Guardian Email Address', null=True)
    guardian_address = models.TextField('Guardian Address', null=True)

class History(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='student_history')
    from_class = models.PositiveIntegerField('From Class', null=True)
    to_class = models.PositiveIntegerField('From Class', null=True)
    from_academic_year = models.CharField('From Academic Year', max_length=9, null=True)
    to_academic_year = models.CharField('To Academic Year', max_length=9, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


# Attendance session
class AttendanceSession(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=2, unique=True)


class Attendance(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name='rel_class_group')
    class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT, related_name='rel_class_name')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='rel_section')
    presence = models.TextField(blank=True)
    absence = models.TextField(blank=True)
    session = models.ForeignKey(AttendanceSession, on_delete=models.PROTECT, related_name='rel_session')
    attendance_date = models.DateField(("Date"), default=now)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.PositiveIntegerField('Created by')

    class Meta:
        unique_together = ('class_group', 'class_name','section','session','attendance_date')