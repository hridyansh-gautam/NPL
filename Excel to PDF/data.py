from json import loads
from generate_pdf import Generator

# create Class object
generator = Generator()

# Call the extraction function
excel_file_name = './excel_files/N21080387_D6.02c_C-06.xlsx'
json_form = generator.excel_to_json(excel_file_name)

# format data for latex code
latex_data = generator.handle_special_chars(loads(json_form))

# store formatted json data in a file
with open('json_latex.json', 'w') as file:
    file.write(latex_data)

#optional vairables
embed_file=True
plot_graph=True

# Create pdf using extracted data
data_to_send = loads(latex_data)
generator.store_signatures(data_to_send)
file_name = generator.sanitize_filename(data_to_send['certificate_no'])
generator.create_pdf(data_to_send, excel_file_name, file_name, embed_file, plot_graph)


# XXXXX_D1.01_C-XXX
# N21080387_D6.02c_C-06
# N23070405_D3.03_C-037
