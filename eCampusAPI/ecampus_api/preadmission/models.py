from django.db import models
from master.models import ClassName, Caste, Gender
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from student.models import Document
from master.services import get_academic_years
from django.conf import settings

class Application(models.Model):
    academic_year = models.CharField('Academic Year', max_length=10)
    application_token = models.CharField('Application token', editable=False, unique=True, max_length=250)
    docs = models.OneToOneField(Document, on_delete=models.PROTECT, null=True)
    student_name = models.CharField('Student Name', validators=[MinLengthValidator(3), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT, null=True)
    dob = models.DateField('Date of Birth')
    class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT)
    father_name =  models.CharField('Father name', validators=[MinLengthValidator(3), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    father_mobile = models.CharField('Father Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True, blank=True)
    mother_name =  models.CharField('Mother name', validators=[MinLengthValidator(3), RegexValidator(regex='^[a-zA-Z ]*$')], max_length=60)
    email_address = models.EmailField('Email Address', null=True)
    mother_mobile = models.CharField('Mother Mobile Number', validators=[RegexValidator(regex='^[\d]{10,12}$')], max_length=12, null=True, blank=True)
    previous_school = models.CharField('Previous School Name', max_length=200, null=True, blank=True)
    primary_contact_person = models.CharField(choices=settings.PRIMARY_CONTACT_CHOICE, max_length=10)
    existing_parent = models.CharField('EXISTING PARENT', choices=settings.EXISTING_PARENT_CHOICES, max_length=3)
    query = models.TextField("Query", max_length=2000, blank=True)
    mode = models.BooleanField('Mode', default=True) #mode represents whether the student is enquired offline or online
    is_verified = models.BooleanField('Is Verified', default=0)
    is_docs_verified = models.BooleanField('Is Docs Verified', default=False)
    is_applied = models.BooleanField('Is Applied', default=0)
    is_admitted = models.BooleanField('Is Admitted', default=0)
    reference_number = models.CharField('Refrence Number', unique=True, max_length=50, null=True)
    created_by = models.IntegerField('Created By', default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-created_on']
