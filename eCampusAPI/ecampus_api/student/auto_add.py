import requests

# data = {
#             "academic_year": "2023_2024",
#             "first_name": "AARVIK ",
#             "dob": "2018-01-01",
#             "father_name": "father",
#             "father_mobile": "9945272775",
#             "father_email": "father@gmail.com",
#             "mother_name": "mother",
#             "primary_contact_person": "father",
#             "is_active": True,
#             "is_verifid": True,
#             "is_docs_verified": False,
#             "is_applied": True,
#             "mode": True,
#             "is_admitted": True,
#             "class_name": "19",
#             "gender": "6",
#             "section": "20",
#             "admission_number": "4",
#             "current_address": "some street",
#             "existing_parent": "yes",
#             "created_by": 1
# }



import requests
import pandas as pd
import json





df = pd.read_excel('ihs_ganesha_building.xlsx', sheet_name="Sheet12")


for index, row in df.iterrows():
    
    data = {
    "academic_year": "2022_2023",
    "first_name": f"{row['first_name']}",
    "last_name" : f"{row['last_name']}",
    "dob": f"{row['dob']}",
    "father_name": f"{row['father_name']}",
    "father_mobile": f"{row['father_mobile']}",
    "father_email": "father@gmail.com",
    "father_qualification": "",
    "father_occupation": "",
    "father_annual_income": "",
    "father_address": "",
    "mother_name": f"{row['mother_name']}",
    "mother_mobile": "",
    "mother_email": "",
    "mother_qualification": "",
    "mother_occupation": "",
    "mother_annual_income": "",
    "mother_address": "",
    "guardian_name": "",
    "guardian_email": "",
    "guardian_address": "",
    "previous_school": "",
    "primary_contact_person": "father",
    "is_active": True,
    "is_verifid": True,
    "is_docs_verified": True,
    "is_applied": True,
    "mode": True,
    "is_admitted": True,
    "class_name": f"{row['class_name']}",
    "gender": f"{row['gender']}",
    "caste": "",
    "caste_category": "",
    "section": f"{row['section']}",
    "quota": "1",
    "religion": "",
    "mother_tongue": "",
    "admission_number": f"{row['admission_number']}",
    "place_of_birth": "",
    "sats_number": f"{row['sats_no']}",
    "combination": "",
    "student_mobile": "",
    "student_email": "",
    "nationality": "",
    "current_address": f"{row['current_address']}",
    "permanent_address": "",
    "existing_parent": "no",
    "created_by": 1,
    "student_aadhar_number": f"{row['student_adhar_no']}"
    }
    
    data['first_name'] = data['first_name'].replace('.', ' ')
    data['last_name'] = data['last_name'].replace('.', ' ')
    
    if data['student_aadhar_number'] == 'nan':
        data['student_aadhar_number'] = ''
    
    if data['sats_number'] == 'nan':
        data['sats_number'] = ''
        
    if data['last_name'] == 'nan':
        data['last_name'] = ''
    
    data['dob'] = data['dob'].strip(' 00:00:00')
    data['father_name'] = data['father_name'].replace('.', ' ')
    data['mother_name'] = data['mother_name'].replace('.', ' ')

    print(data['admission_number'])
 
    response = requests.post('http://localhost:8000/student/add-existing-student/', json=data)
    print(response.json())
    
    
