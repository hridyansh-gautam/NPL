import pandas as pd
import json
import generate_pdf
import re

# Handle Subscript and Superscript characters in text
def replace_sub_superscript(text):
    # Replace superscript (^number) with actual superscript notation
    text = re.sub(r'[\u2070-\u2079]', lambda x: f'\\textsubscript{{{ord(x.group(0)) - 8304}}}', text)
    # Replace subscript (₀₁₂₃₄₅₆₇₈₉) with _number format
    text = re.sub(r'[\u2080-\u2089]', lambda x: f'\\textsubscript{{{ord(x.group(0)) - 8320}}}', text)
    
    return text

# Extact Measurement data from the excel sheet
def extract_measurement_data(df):
    tables = []  # List to hold all the extracted tables
    table = []  # Current table being processed
    header = None  # Header of the current table
    
    # Iterate through each row in the dataframe
    for i, row in df.iterrows():
        if row.isnull().all():  # Check if the row is completely empty
            if table:  # If there is a current table being processed
                if header is not None:  # If header is set
                    table_df = pd.DataFrame(table, columns=header)
                    tables.append(table_df.dropna(axis=1, how='all'))  # Add the table to tables list
                table = []  # Reset table
                header = None  # Reset header
        else:
            if header is None:  # If header is not set
                header = row.tolist()  # Set the current row as header
            else:
                table.append(row.tolist())  # Add row to the current table

    latex_tables = ''
    # Convert each table to LaTeX format
    for i, table in enumerate(tables):
        col_count = len(table.columns)
        col_width = 19 / col_count
        col_format = ''.join([f'|>{{\\centering}}p{{{col_width}cm}}' for _ in range(0, col_count - 1)])
        tex = table.to_latex(
            multicolumn=True, 
            header=True, 
            index=False,
            longtable=True,
            column_format= col_format + f'|>{{\\centering\\arraybackslash}}p{{{col_width}cm}}|',  
            caption=f"This is Table {i + 1}"
        )
        # Replace default formatting with desired formatting
        tex = tex.replace('\\toprule', '').replace('\\midrule', '').replace('\\bottomrule', '')
        tex = tex.replace('\\\n', '\\ \\hline\n')
        latex_tables += tex
        print(f"Table {i + 1} created.")  # Log the table creation
    return latex_tables


# Extract administrative and measurement data from Excel file to json
def excel_to_json(excel_file):
    xls = pd.ExcelFile(excel_file)
    sheet_names = xls.sheet_names
    result = {}

    # Iterate through each sheet in the Excel file
    for sheet_name in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        for row in df.values:
            value = str('' if pd.isna(row[1]) else row[1])
            value = replace_sub_superscript(value)
            if row[0] == 'result_table':
                result['result_table'] = extract_measurement_data(df)
            elif not pd.isna(row[0]):
                value = value.replace('\n', ' \\\\\n').replace(']', ']}').replace('[', '{[')
                result[str(row[0])] = value
    
    result['doi_no'] = 'X'
    return json.dumps(result, indent=4)

    
# Convert special characters in data to suitable Latex format
def json_to_latex(data):
    for key, val in data.items():
        val = val.replace('%', '\\%').replace('#', '\\#').replace('^', '\\^')
        val = val.replace('\u2103', '\\textdegree C').replace('\u03a9', '\\textohm').replace('\u00b1', ' \\textpm ')
        data[key] = val
    return json.dumps(data, indent=4)


def sanitize_filename(filename):
    # Define a regex pattern for disallowed characters
    disallowed_chars = r'[\/:*?"<>|]'
    # Replace disallowed characters with an underscore
    sanitized_filename = re.sub(disallowed_chars, '_', filename)
    return sanitized_filename

# Call the extraction function
excel_file_name = './excel_files/N23070405_D3.03_C-037.xlsx'
json_form = excel_to_json(excel_file_name)

# format data for latex code
latex_data = json_to_latex(json.loads(json_form))

# store formatted json data in a file
with open('json_latex.json', 'w') as file:
    file.write(latex_data)

# Create pdf using extracted data
data_to_send = json.loads(latex_data)
file_name = sanitize_filename(data_to_send['certificate_no'])
generate_pdf.create_pdf(data_to_send, excel_file_name, file_name)





# # Generate Checksum
# expected_checksum = generate_pdf.generate_checksum(pdf_name)
# print(f"Generated checksum for {pdf_name}: {expected_checksum}")
# # Verify the checksum
# verification_result = generate_pdf.verify_checksum(pdf_name, expected_checksum)
# print(f"Checksum verification for {pdf_name}: {verification_result}")

