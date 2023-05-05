from student.models import Profile as student_profile


class AttendanceValidator(object):
    
    def __init__(self, validate_data):
        self.request = validate_data
        self.presence = validate_data.get('presence', None)
        self.absence = validate_data.get('absence', None)
        self.is_error = False
        self.error_message = []

    def validator(self):
        self.isAttendanceEmpty()
        if not self.is_error:
            self.isAnyDuplicate()
        if not self.is_error:
            self.isTotalCountMatch()
        if not self.is_error:    
            self.callListCompare()
        return self.is_error, self.error_message

    def isAttendanceEmpty(self):
        if not self.presence and not self.absence:
            self.is_error = True
            self.error_message.append('Presence and Absence id list cannot be empty!')

    def isAnyDuplicate(self):
        match_list = list(set(self.presence) & set(self.absence))
        if(len(match_list) >= 1):
            self.is_error = True
            match_list = [str(i) for i in match_list]
            self.error_message.append('Found Duplicate Id in both Presence and Absence ID list : '+str(','.join(match_list)))

    def isTotalCountMatch(self):
        student_count = student_profile.objects.filter(
                        class_group_id=self.request.get('class_group'),
                        class_name_id=self.request.get('class_name'),
                        section_id=self.request.get('section')
                    ).count()
        students_strgenth = self.presence + self.absence
        if(len(students_strgenth) != student_count):
            self.is_error = True
            self.error_message.append('Sum of Presence and absence ids are not matched with Total student strgenth')

    def callListCompare(self):
        if len(self.presence) > 0:
                self.listCompare(self.presence, 'Presence',self.request)
            
        if len(self.absence) > 0:
            self.listCompare(self.absence, 'Absence', self.absence)

    def listCompare(self, list_var, preciseattendance, validate_data):
        get_list_db = student_profile.objects.values('id').filter(
            id__in=list_var,
            class_group_id=self.request.get('class_group'),
            class_name_id=self.request.get('class_name'),
            section_id=self.request.get('section')
        )
        get_list = [i['id'] for i in get_list_db]
        list_var = list(set(list_var)-set(get_list))
        if(len(list_var) >=1):
            self.is_error = True
            self.error_message.append(str(preciseattendance)+' list - Student IDs are invalid:' +str(list_var))
