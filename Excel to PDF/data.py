from json import loads
import generate_pdf

# Call the extraction function
excel_file_name = './excel_files/N23070405_D3.03_C-037.xlsx'
json_form = generate_pdf.excel_to_json(excel_file_name)

# format data for latex code
latex_data = generate_pdf.handle_special_chars(loads(json_form))

# store formatted json data in a file
with open('json_latex.json', 'w') as file:
    file.write(latex_data)

# Create pdf using extracted data
data_to_send = loads(latex_data)
file_name = generate_pdf.sanitize_filename(data_to_send['certificate_no'])
generate_pdf.create_pdf(data_to_send, excel_file_name, file_name)
