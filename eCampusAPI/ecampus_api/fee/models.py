from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from master.models import ClassName, Section, Quota
from fee.validators import fee_type_name_validator
from student.models import Profile
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
_UNSAVED_1 = 'unsaved_1'


def get_upload_path(instance, file_name):
  return "uploads/fee-category/{0}/{1}".format(instance.pk, file_name)


class FeeType(models.Model):
  fee_type = models.CharField('Fee Type', choices=settings.FEE_TYPE_CHOICES, max_length=60)
  fee_type_name = models.CharField('Fee Type Name', unique=True, max_length=120, validators=[fee_type_name_validator])
  created_on = models.DateTimeField(auto_now_add=True, null=True)
  created_by = models.IntegerField('created by')

  class Meta:
      ordering = ['-created_on']


class FeeCategory(models.Model):
  fee_category = models.CharField('Fee Category', max_length=120)
  company_name = models.CharField('Company Name', max_length=120)
  logo = models.ImageField('Photo', upload_to=get_upload_path,
                                    validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], null=True)
  address = models.TextField(null=True)
  address_two = models.TextField(null=True)
  address_three = models.TextField(null=True)
  address_four = models.TextField(null=True)
  created_on = models.DateTimeField(auto_now_add=True, null=True)
  created_by = models.IntegerField('created by')

  class Meta:
      ordering = ['-created_on']


@receiver(pre_save, sender=FeeCategory)
def skip_saving_file(sender, instance, **kwargs):
    if not instance.pk:
        if not hasattr(instance, _UNSAVED_1):
            setattr(instance, _UNSAVED_1, instance.logo)
            instance.logo = None


@receiver(post_save, sender=FeeCategory)
def save_file(sender, instance, created, **kwargs):
        if created:
            if hasattr(instance, _UNSAVED_1):
                instance.logo = getattr(instance, _UNSAVED_1)
            instance.save()
            # delete it if you feel uncomfortable...
            instance.__dict__.pop(_UNSAVED_1)


class FeeToClass(models.Model):
  start_date = models.DateField('Start Date')
  end_date = models.DateField('End Date')
  student = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
  class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT, null=True)
  section = models.ForeignKey(Section, on_delete=models.PROTECT, null=True)
  quota = models.ForeignKey(Quota, on_delete=models.PROTECT)
  fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT)
  fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT)
  new_student_amount = models.DecimalField('New Student Amount', max_digits=10, decimal_places=2, default=0)
  old_student_amount = models.DecimalField('Old Student Amount', max_digits=10, decimal_places=2, default=0)
  created_on = models.DateTimeField(auto_now_add=True, null=True)
  created_by = models.IntegerField('created by')
  academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')])
  month = models.DateField(null=True, blank=True) #helps in identifying which month fees belongs to.
  class Meta:
      ordering = ['-created_on']


class PaymentMode(models.Model):
  name = models.CharField(max_length=215)
  created_on = models.DateTimeField(auto_now_add=True, null=True)
  created_by = models.IntegerField('created by')

  class Meta:
      ordering = ['-created_on']


class FeeConcession(models.Model):
  concession_amount = models.DecimalField('Concession Amount', max_digits=10, decimal_places=2)
  student_id = models.ForeignKey(Profile, on_delete=models.PROTECT)
  fee_to_class = models.ForeignKey(FeeToClass, on_delete=models.PROTECT)
  is_valid = models.BooleanField('Valid', default=True)
  academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')])
  created_on = models.DateTimeField(auto_now_add=True)
  created_by = models.IntegerField('created by', null=True)

  class Meta:
      ordering = ['-created_on']


class FeeCollection(models.Model):
  student_id = models.ForeignKey(Profile, on_delete=models.PROTECT)
  # fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT)
  # fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT)
  fee_to_class = models.ForeignKey(FeeToClass, on_delete=models.PROTECT)
  fee_amount = models.DecimalField('Fee Amount', max_digits=10, decimal_places=2, default=0)
  concession_amount = models.DecimalField('Concession Amount', max_digits=10, decimal_places=2, default=0)
  concession = models.ForeignKey(FeeConcession, on_delete=models.PROTECT, null=True)
  total_payable_amount = models.DecimalField('Total Payable Amount', max_digits=10, decimal_places=2,  default=0)
  paid_amount = models.DecimalField('Paid Amount', max_digits=10, decimal_places=2,  default=0)
  balance_amount = models.DecimalField('Balance Amount', max_digits=10, decimal_places=2, default=0)
  payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
  academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')])
  fee_denomination = models.TextField(null=True)
  remarks = models.TextField()
  created_on = models.DateTimeField(auto_now_add=True)
  created_by = models.IntegerField('created by', null=True)

  class Meta:
      ordering = ['-created_on']



# class OldFee(models.Model):
#   student_id = models.ForeignKey(Profile, on_delete=models.PROTECT)
#   fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT)
#   fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT)
#   old_fee_amount = models.DecimalField('Fee Amount', max_digits=10, decimal_places=2, default=0)
#   academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')])
#   is_paid = models.BooleanField('is Paid', default=False)
#   created_on = models.DateTimeField(auto_now_add=True)
#   created_by = models.IntegerField('created by')

#   class Meta:
#       ordering = ['-created_on']

class FeeBillRepo(models.Model):
  fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT)
  accounting_start = models.DateField('Accounting Start')
  accounting_end = models.DateField('Accounting End')
  last_bill_number = models.PositiveIntegerField('Last Bill Number', default=0)
  created_on = models.DateTimeField(auto_now_add=True, null=True)


class FeeMasterCollection(models.Model):
  student = models.ForeignKey(Profile, on_delete=models.PROTECT)
  fee_collections = models.TextField()
  total_paid_amount = models.DecimalField('Total Paid Amount', max_digits=10, decimal_places=2,  default=0)
  payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
  remarks = models.TextField()
  bill_number = models.CharField(max_length=250)
  uuid = models.CharField(unique=True, max_length=250)
  academic_year = models.CharField(max_length=9, validators=[MinLengthValidator(9), RegexValidator(regex='^[0-9_]*$')], default='2021_2022')
  fee_category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, null=True)
  created_on = models.DateField(auto_now_add=True)
  created_by = models.IntegerField('created by')
