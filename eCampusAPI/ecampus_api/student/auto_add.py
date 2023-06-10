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





df = pd.read_excel('school_data.xlsx', sheet_name="Sheet10")


for index, row in df.iterrows():
    
    data = {
    "academic_year": "2022_2023",
    "first_name": f"{row['first_name']}",
    "dob": "2008-01-01",
    "father_name": "father",
    "father_mobile": f"{row['father_mobile']}",
    "father_email": "father@gmail.com",
    "father_qualification": "",
    "father_occupation": "",
    "father_annual_income": "",
    "father_address": "",
    "mother_name": "mother",
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
    "is_docs_verified": False,
    "is_applied": True,
    "mode": True,
    "is_admitted": True,
    "class_name": f"{row['class_name']}",
    "gender": f"{row['gender']}",
    "caste": "",
    "caste_category": "",
    "section": f"{row['section']}",
    "quota": "",
    "religion": "",
    "mother_tongue": "",
    "admission_number": f"{row['admission_number']}",
    "place_of_birth": "",
    "sats_number": "",
    "combination": "",
    "student_mobile": "",
    "student_email": "",
    "nationality": "",
    "current_address": "some street",
    "permanent_address": "",
    "existing_parent": "no",
    "created_by": 1
    }
    
    print(row["admission_number"])
    
    response = requests.post('http://localhost:8000/student/add-existing-student/', json=data)
    print(response.json())
