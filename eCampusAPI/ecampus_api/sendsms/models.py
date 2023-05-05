from django.db import models


class Template(models.Model): #add, update, delete, get, list
    template_name = models.CharField('template name',max_length=60)
    template_content = models.TextField('content message')
    dlt_template_id = models.TextField('DLT ID')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by  = models.IntegerField('CreatedBy')
    updated_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField('Updated By')

    class Meta:
        ordering = ['-id']


class Group(models.Model):
    name = models.CharField('Group name', max_length=60)
    students = models.TextField('Students')
    class_groups = models.TextField('Class Groups')
    classes = models.TextField('Classes')
    sections = models.TextField('Sections')
    employees = models.TextField('Sections')
    employee_groups = models.TextField('Sections')
    members = models.TextField('Group members')
    count = models.IntegerField('Total members')
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by  = models.IntegerField('Created by')
    updated_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.IntegerField('Updated by')
    status = models.BooleanField('Group status', default=True)

    class Meta:
        ordering = ['-id']


class SMSTracker(models.Model):
    template_id = models.IntegerField('DLT Template id', null=True)
    student_id = models.TextField('Student Id', null=True)
    class_id = models.TextField('Class Id', null=True)
    class_group = models.TextField('Class Group', null=True)
    section = models.TextField('Section', null=True)
    employee_id = models.TextField('Employee Id', null=True)
    employee_department_id = models.TextField('Category Id', null=True)
    addtional_numbers = models.TextField('Addtional numbers', null=True)
    reference_number = models.CharField('Reference Number', unique=True, max_length=20)
    message_content = models.TextField('Message Content', null=True)
    client_request = models.TextField('Request data')
    vendor_response = models.TextField('Vendor Response', null=True)
    batch_id = models.CharField('Batch id info',max_length=20, null=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, null=True, related_name='sms_group')
    client_request_status = models.BooleanField(default=True)
    vendor_reponse_status = models.BooleanField(default=False)
    vendor_warning = models.TextField('Vendor warning', null=True)
    vendor_error = models.TextField('Vendor Error', null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by  = models.IntegerField('Created by')

    class Meta:
        ordering = ['-id']
