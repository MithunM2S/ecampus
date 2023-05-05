from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from base import validators
from django.core.validators import FileExtensionValidator


# Validators
trust_name_validator = RegexValidator(r'^[a-zA-Z ]+$', 'only valid trust name is required')
institution_name_validator = RegexValidator(r'^[a-zA-Z ]+$', 'only valid institution name is required')
address_validator = RegexValidator(r'^(\w *\s*[\  # \-\,\/\.\(\)\&]*)+$', 'only valid address is required')
class_group_validator = RegexValidator(r'^[a-zA-Z- ]+$', 'only valid class group is required')
class_name_validator = RegexValidator(r'^[a-zA-Z0-9- ]+$', 'only valid class name is required')
section_name_validator = RegexValidator(r'^[a-zA-Z0-9- ]+$', 'only valid section name is required')
category_validator = RegexValidator(r'^[a-zA-Z0-9-/() ]+$', 'only valid category is required')
caste_validator = RegexValidator(r'^[a-zA-Z() ]+$', 'only valid caste name is required')


def get_upload_path(instance, file_name):
  return "uploads/institution-profile/{0}/{1}".format(instance.pk, file_name)


class Profile(models.Model):
    trust_name = models.CharField('Trust Name', unique=True, max_length=60, validators=[trust_name_validator])
    institution_name = models.CharField('Institution Name', unique=True, max_length=60, validators=[trust_name_validator])
    address1 = models.TextField('Address1')
    address2 = models.TextField('Address2')
    phone_number = PhoneNumberField(unique=True)
    administrator = models.CharField('Administrator', max_length=120)
    mobile_number = PhoneNumberField(unique = True)
    running_academic_start = models.DateField('Running Academic Start', default='2020-02-02')
    running_academic_end = models.DateField('Running Academic End', default='2020-02-02')
    upcoming_academic_start = models.DateField('Upcoming Academic Start', default='2020-02-02')
    upcoming_academic_end = models.DateField('Upcoming Academic End', default='2020-02-02')
    financial_start = models.DateField('Financial Start')
    financial_end = models.DateField('Financial End')
    is_active = models.BooleanField(default=True)
    logo = models.ImageField('Logo', upload_to=get_upload_path,
                                    validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created by')
 
class RoomManagement(models.Model):
    pass

class ClassGroup(models.Model):
    class_group = models.CharField(unique=True, max_length=100, validators=[class_group_validator])
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created_by')

class ClassName(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name='choose_classgroup')
    class_name = models.CharField(unique=True, max_length=100, validators=[class_name_validator])
    from_age = models.FloatField('from_age')
    to_age = models.FloatField('to_age')
    class_code = models.CharField(max_length=3, unique=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created_by')

class Section(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name='choose_section_classgroup')
    class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT, related_name='choose_classname')
    section_name = models.CharField(max_length=100, validators=[section_name_validator])
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created_by')

class CasteCategory(models.Model):
    category = models.CharField(unique=True, max_length=20, validators=[category_validator])
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created_by')

class Caste(models.Model):
    category = models.ForeignKey(CasteCategory, on_delete=models.PROTECT, related_name='choose_category')
    caste = models.CharField(unique=True, max_length=100, validators=[caste_validator])
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.IntegerField('created_by')

class Repo(models.Model):
    admission_number  = models.IntegerField(default=0)
    admission_academic_year = models.CharField(max_length=9)
    reference_number  = models.IntegerField(default=0)
    academic_year = models.CharField(max_length=9)

class Subject(models.Model):
    name = models.CharField('Subject Name', max_length=50, unique=True)
    code = models.CharField('Subject Code', max_length=15, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField('created_by')

class RepoClass(models.Model):
    admission_academic_year = models.CharField(max_length=9)
    cid = models.ForeignKey(ClassName, on_delete=models.PROTECT, related_name='class_academic_year')
    max_strength = models.PositiveIntegerField(default=500)
    available_strength = models.PositiveIntegerField(default=500)
    created_on = models.DateTimeField(auto_now_add=True)

class Gender(models.Model):
    gender = models.CharField(max_length=20, validators=[validators.alpha_space], unique=True)

class Quota(models.Model):
    name = models.CharField(max_length=80, validators=[validators.alpha_space], unique=True)

class Religion(models.Model):
    name = models.CharField(max_length=100, validators=[validators.alpha_space], unique=True)

class MotherTongue(models.Model):
    name = models.CharField(max_length=150, validators=[validators.alpha_space], unique=True)

class GroupConcat(models.Aggregate):

    function = 'GROUP_CONCAT'
    template = "%(function)s(%(distinct)s %(expressions)s %(separator)s)"

    def __init__(self, expression, distinct=False, separator=',', **extra):
        super(GroupConcat, self).__init__(
            expression,
            distinct='DISTINCT' if distinct else '',
            separator="SEPARATOR '%s'" % separator,
            output_field=models.CharField(),
            **extra
        )


class AcademicYear(models.Model):
    academic_year = models.CharField(max_length=9)
    start = models.DateField('Running Academic Start', default='2020-02-02')
    end = models.DateField('Running Academic End', default='2020-02-02')
