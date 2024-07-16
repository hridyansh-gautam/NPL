# from json import loads
from generate_pdf import Generator

# create Class object
generator = Generator()

# # Call the extraction function
# excel_file_name = './excel_files/N19110969_D1.06_T-272.xlsx'
# json_form = generator.excel_to_json(excel_file_name)

# # format data for latex code
# latex_data = generator.handle_special_chars(loads(json_form))

# # store formatted json data in a file
# with open('json_latex.json', 'w') as file:
#     file.write(latex_data)

# doc_type='testing' # 1 for calibration, 2 for testing report
# # Create pdf using extracted data
# data_to_send = loads(latex_data)
# generator.store_signatures(data_to_send)

# dict_template = {
#     "report_name": "",
#     "device_name":"",
#     "certificate_no":"",
#     "end_date": "",
#     "report_no": "",
#     "next_date":"",
#     "tested_for": "",
#     "calibrated_for": "",
#     "description": "",
#     "env_conditions": "",
#     "stds_used": "",
#     "tracability": "",
#     "procedure": "",
#     "tested_by": "",
#     "calibrated_by": "",
#     "checked_by": "",
#     "incharge": "",
#     "issued_by": "",
#     "result_table": "",
#     "result_desc": "",
#     "testing_date": "",
#     "calibration_date": "",
#     "remarks": "",
#     "doi_no": "",
# }

# for key in dict_template:
#     if key in data_to_send:
#         dict_template[key] = data_to_send[key]
# # print(dict_template)
# file_name = generator.sanitize_filename(data_to_send['certificate_no'] if doc_type=='calibration' else (data_to_send['report_no']))
# generator.create_pdf(dict_template, excel_file_name, file_name, attach_data=True, attach_graph=True,doc_type=doc_type)

generator.execute_pdf_generator(excel_file='./excel_files/N19110969_D1.06_T-272.xlsx', doc_type='testing', attach_data=True, attach_graph=True)

# XXXXX_D1.01_C-XXX
# N21080387_D6.02c_C-06
# N23070405_D3.03_C-037
