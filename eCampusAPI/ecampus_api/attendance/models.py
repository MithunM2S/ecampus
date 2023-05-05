from django.db import models
from master.models import ClassGroup, ClassName,  Section
from django.db.models.functions import Now
import datetime
from django.utils.timezone import now

class AttendanceSession(models.Model):
    session_name = models.CharField(max_length=20)
    session_code = models.CharField(max_length=2, unique=True)


class AttendanceTracker(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT)
    class_name = models.ForeignKey(ClassName, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    presence = models.TextField(blank=True)
    absence = models.TextField(blank=True)
    session = models.ForeignKey(AttendanceSession, on_delete=models.PROTECT) 
    attendance_date = models.DateField(("Date"), default=now) #USE MYSQL FUNCTION 
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('class_group', 'class_name','section','session','attendance_date')