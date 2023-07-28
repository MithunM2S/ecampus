import pandas as pd

excel_file = pd.ExcelFile('school_data.xlsx')

sheet_names = excel_file.sheet_names

# Iterate through the sheet names and print them
for sheet_name in sheet_names:
    print(sheet_name)