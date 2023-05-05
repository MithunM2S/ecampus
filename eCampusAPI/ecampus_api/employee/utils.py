from .models import *
from datetime import date


class DashboardService(object):
    def __init__(self):
        self.departments = Department.objects.values_list('name', flat=True)
        self.today = date.today()

    def get_dep_wise_emp_count(self):
        att_data = Attendance.objects.filter(attendance_date=self.today)
        if att_data:
            present_count = len(att_data[0].presence)
            absent_count = len(att_data[0].absence)
        else:
            present_count = 0
            absent_count = 0

        result = [
            {
                'Total': EmployeeDetails.objects.all().count(),
                'present':present_count,
                'absent':absent_count}]
        for each in self.departments:
            each_data_count = EmployeeDetails.objects.filter(
                department__name=each).count()
            each_data = Attendance.objects.filter(attendance_date=self.today, department__name=each)
            if each_data:
                present = len(each_data[0].presence)
                absent = len(each_data[0].absence)
            else:
                present = 0
                absent = 0
            
            # present = Attendance.objects.filter(
            #     attendance_date=self.today,
            #     attendance_status='Present',
            #     employee_details__department__name=each).count()
        
            # absent = Attendance.objects.filter(
            #     attendance_date=self.today,
            #     attendance_status='Absent',
            #     employee_details__department__name=each).count()
            result.append(
                {each: each_data_count, 'present': present, 'absent': absent})
        return result
