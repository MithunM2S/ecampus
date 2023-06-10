from master import services
from django.db.models import Q, Count, F
from master.models import Repo, ClassGroup, ClassName, GroupConcat, Section
from student.models import Profile
from master import services as master_services


class ProfileCountService(object):

    # init method or constructor
    def __init__(self, admission_academic_year=None):
        if admission_academic_year:
            self.filter_admission_academic_year = admission_academic_year
        else:
            self.filter_admission_academic_year = services.get_academic_years_key_value('running')[0]
        self.queryset = Profile.objects

    # Get total student count
    # def get_total_student_count(self):
    #     total_profile_count = self.queryset.count()
    #     return total_profile_count

    # Get new student count
    # def get_new_student_count(self):
    #     new_student_count = self.queryset.count()
    #     return new_student_count

    # Get old student count
    def get_old_student_count(self):
        old_student_count = self.queryset.filter(~Q(admission_academic_year=self.filter_admission_academic_year)).count()
        return old_student_count

    def get_cards_count(self):
        #queryset is a just a manager object of a profile
        
        cards = self.queryset.values('admission_academic_year').order_by().annotate(
            total_student= Count('id'),
            new_student= Count('id', filter=Q(admission_academic_year=self.filter_admission_academic_year)),
        )
    
        
        '''
        The cards variable look something like this for the academic_year 2023_2024
        <QuerySet [{'admission_academic_year': '2023_2024', 'total_student': 410, 'new_student': 410}]>
        '''

        old_student = self.get_old_student_count()
        if cards: #bugs in the code needs to be fixed 
            print(cards, 'ok')
            del cards[0]['admission_academic_year']
            cards[0]['old_student'] = old_student
            cards[0]['new_student'] = cards[1]['new_student']
            cards[0]['total_student'] += cards[1]['total_student']
            data = cards
            # print(data)
        else:
            data = [{"old_student": old_student}]
        return data

    # Get Class group wise count 
    def get_class_group_wise_student_count(self):
        class_groupwise_student_count = []
        for classGroupObject in ClassGroup.objects.all():
            count = self.queryset.filter(class_name__in=ClassName.objects.filter(class_group=classGroupObject.id)).count()
            class_data = []
            for classObject in ClassName.objects.filter(class_group=classGroupObject.id):
                section_data = []
                for sectionObject in Section.objects.filter(class_name=classObject.id):
                    section_data.append({"id": sectionObject.id, "name": sectionObject.section_name, "count": self.queryset.filter(section=sectionObject.id).count()})
                class_data.append({"id": classObject.id, "name": classObject.class_name, "count": self.queryset.filter(class_name=classObject.id).count(), "section": section_data})
            class_groupwise_student_count.append({"id": classGroupObject.id, "name":classGroupObject.class_group, "count":count, "class": class_data})
        return class_groupwise_student_count

    # Get Class wise count 
    def get_class_wise_student_count(self):
        class_wise_student_count = []
        for cname in ClassName.objects.select_related('class_group').all():
            count = self.queryset.filter(class_name=cname.id).count()
            class_wise_student_count.append({"id":cname.id, "class_name":cname.class_name, "count": count})
        return class_wise_student_count

    # Get Section wise count 
    def get_section_wise_student_count(self):
        section_wise_student_count = []
        for section in Section.objects.select_related('class_group', 'class_name').all():
            count = self.queryset.filter(class_name=section.id).count()
            data = {
                "id":section.id,
                "section_name":section.section_name,
                "count": count,
                "class": {
                    "id": section.class_name.id,
                    "name": section.class_name.class_name
                },
                "class_group": {
                    "id": section.class_group.id,
                    "name": section.class_group.class_group,
                }
            }
            section_wise_student_count.append(data)
        return section_wise_student_count

    # Get academic year wise student count
    def get_yearly_admission_count(self):
        academic_year_wise_count = self.queryset.values(year=F('admission_academic_year')).annotate(count=Count('admission_academic_year')).order_by('admission_academic_year')
        return academic_year_wise_count

def get_student_state(student_id):
    '''
    Function which helps to determine whether the student is old or new
    '''
    
    try:
        student = Profile.objects.values('id', 'class_name', 'section', 'quota', 'admission_academic_year').get(id=student_id)
        run_academic_year = master_services.get_academic_years_key_value('running')[0]
        up_academic_year = master_services.get_academic_years_key_value('upcoming')[0]
        admission_academic_year = student.get('admission_academic_year')
        if admission_academic_year == run_academic_year or admission_academic_year == up_academic_year:
            state = 'new_student'
        else :
            state = 'old_student'
        return state
    except Exception as e:
        return None

def get_student(student_id):
    try:
        student = Profile.objects.get(id=student_id, is_active=True)
        return student
    except Exception as e:
        return None
    

def delete_null_keys_if_present(request_data):
    '''
    This function is used to delete the keys of the 
    empty string of the json sent from the frontend
    so that later we can send it for the serializer
    '''
    cleaned_request_data = request_data
    keys_to_delete = []
    for key in request_data:
        if len(str(request_data[key]).strip()) == 0:
            keys_to_delete.append(key)
    
    if keys_to_delete:  
        for key in keys_to_delete:
            del cleaned_request_data[key]
        return cleaned_request_data
    
    return cleaned_request_data
    
            
