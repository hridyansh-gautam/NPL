import subprocess
import os
import hashlib
import re
import pandas as pd
import json
from db_access import add_checksum, get_signature
import numpy as np
import cv2

class Generator:
    def sanitize_filename(self, filename):
        """
        Sanitize the filename by replacing disallowed characters with an underscore.

        :param filename: The original filename.
        :return: The sanitized filename.
        """

        # Define a regex pattern for disallowed characters
        disallowed_chars = r'[\/:*?"<>|]'
        # Replace disallowed characters with an underscore
        sanitized_filename = re.sub(disallowed_chars, "_", filename)
        return sanitized_filename

    
    def generate_checksum(self, file_path, algorithm="sha256"):
        """
        Generate a checksum for a given file using the specified algorithm.

        :param file_path: Path to the file.
        :param algorithm: Hashing algorithm to use (default: 'sha256').
        :return: Checksum of the file.
        """
        hash_function = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            while chunk := f.read():
                hash_function.update(chunk)
        return hash_function.hexdigest()

    
    def extract_measurement_data(self, df):
        """
        Extract measurement data from an Excel sheet and convert it to LaTeX format tables.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the Excel sheet data.

        Returns:
        str: The LaTeX formatted tables as a string.
        """
        tables = []  # List to hold all the extracted tables
        table = []  # Current table being processed
        header = None  # Header of the current table

        # Iterate through each row in the dataframe
        for i, row in df.iterrows():
            if row.isnull().all():  # Check if the row is completely empty
                if table:  # If there is a current table being processed
                    if header is not None:  # If header is set
                        table_df = pd.DataFrame(table, columns=header)
                        tables.append(
                            table_df.dropna(axis=1, how="all")
                        )  # Add the table to tables list
                    table = []  # Reset table
                    header = None  # Reset header
            else:
                if header is None:  # If header is not set
                    header = row.tolist()  # Set the current row as header
                else:
                    table.append(row.tolist())  # Add row to the current table

        latex_tables = ""
        # Convert each table to LaTeX format
        for i, table in enumerate(tables):
            col_count = len(table.columns)
            col_width = 19 / col_count
            col_format = "".join(
                [f"|>{{\\centering}}p{{{col_width}cm}}" for _ in range(0, col_count - 1)]
            )
            tex = table.to_latex(
                multicolumn=True,
                header=True,
                index=False,
                longtable=True,
                column_format=col_format
                + f"|>{{\\centering\\arraybackslash}}p{{{col_width}cm}}|",
                caption=f"This is Table {i + 1}",
            )
            # Replace default formatting with desired formatting
            replacements = {
                "\\toprule": "",
                "\\midrule": "",
                "\\bottomrule": "",
                "\\\n": "\\ \\hline\n",
                "{Continued on next page} \\\\ \\hline":"{Continued on next page} \\\\",
            }

            def replace_func(match):
                return replacements[match.group(0)]

            pattern = re.compile("|".join(re.escape(k) for k in replacements))
            latex_tables += pattern.sub(replace_func, tex)
            print(f"Table {i + 1} created.")  # Log the table creation
        return latex_tables


    def convert_to_siunitx(self, text):
        # Define the N variable for number matching
        N = r'((\-)?\d+(\.\d+)?)'
        pattern = fr'(\(|)({N}|) (±|to) ({N})( [x] 10{N})?(\)|) (?!.*%)([µ]?\w+)'
        #((\(|)({N}|) (±|to) ({N})( [x] 10{N})?(\)|) (?!.*%)([µ]?\w+)| )({N}) ([µ]?\w+)

        # Search for the pattern
        matches = re.findall(pattern, text)

        # Replace the matches
        replacements = {'':''}
        for match in matches:
            unit = match[-1]
            si_format = f'\\si{{{unit}}}'
            replacements[unit] = si_format

        def replace_func(matched):
            return replacements[matched.group(0)]

        pattern = re.compile("|".join(re.escape(k) for k in replacements))
        result = pattern.sub(replace_func, text)
        
        return result

    def excel_to_json(self, excel_file):
        """
        Extract administrative and measurement data from an Excel file and convert it to JSON format.

        Parameters:
        excel_file (str): The path to the Excel file.

        Returns:
        str: The JSON formatted data as a string.
        """
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        result = {}

        # Iterate through each sheet in the Excel file
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            for row in df.values:
                value = str("" if pd.isna(row[1]) else row[1])
                value = self.handle_sub_superscript(value)
                value = self.convert_to_siunitx(value)
                if row[0] == "result_table":
                    result["result_table"] = self.extract_measurement_data(df)
                elif not pd.isna(row[0]):
                    value = (
                        value.replace("\n", " \\\\\n").replace("]", "]}").replace("[", "{[")
                    )   
                    result[str(row[0])] = value

        result["doi_no"] = "X"
        return json.dumps(result, indent=4)

    
    def handle_special_chars(self, data):
        """
        Convert special characters in data to suitable LaTeX format.

        Parameters:
        data (dict): The dictionary containing the data with special characters.

        Returns:
        str: The JSON formatted data with special characters converted to LaTeX format.
        """
        for key, val in data.items():
            replacements = {
                "%": "\\%",
                "#": "\\#",
                "^": "\\^",
                "\u2103": "\\textdegree C",
                "\u03a9": "\\textohm",
                "\u00b1": " \\textpm ",
                "\\multicolumn{4}{r}{Continued on next page} \\\\ \\hline\n":" ",
            }

            def replace_func(match):
                return replacements[match.group(0)]

            pattern = re.compile("|".join(re.escape(k) for k in replacements))
            data[key] = pattern.sub(replace_func, val)
            #print (data)
        return json.dumps(data, indent=4)

    
    def handle_sub_superscript(self, text):
        """
        Handle subscript and superscript characters in a string and convert them to LaTeX format.

        Parameters:
        text (str): The input text containing subscript and superscript characters.

        Returns:
        str: The text with subscript and superscript characters converted to LaTeX format.
        """
        # Replace superscript (^number) with actual superscript notation
        text = re.sub(
            r"[\u2070-\u2079]",
            lambda x: f"\\textsubscript{{{ord(x.group(0)) - 8304}}}",
            text,
        )
        # Replace subscript (₀₁₂₃₄₅₆₇₈₉) with _number format
        text = re.sub(
            r"[\u2080-\u2089]",
            lambda x: f"\\textsubscript{{{ord(x.group(0)) - 8320}}}",
            text,
        )
        return text

    def store_signatures(self, data):
        """
        Store signatures as images in the 'signatures' directory.

        This method retrieves signatures based on the names provided in the 'data' dictionary
        and stores them as images. If a signature is not found, a blank image is saved instead.

        Parameters:
        data (dict): The dictionary containing the signature names and corresponding data.

        Returns:
        None
        """
        img_names = ['calibrated_by', 'checked_by', 'incharge', 'issued_by']
        blank_img = np.ones((150, 300, 3), dtype=np.uint8) * 255
        for name in img_names:
            sign = get_signature(name=data[name].lower())
            if sign:
                with open(f'signatures/{name}.jpg', 'wb') as img:
                    img.write(sign)
            else:
                cv2.imwrite(f'signatures/{name}.jpg', blank_img)

    def create_pdf(self, data, embed_file, certificate_name, attach_data, attach_graph,doc_type):
        """
        Create a PDF using the provided data and LaTeX template, and optionally embed a file.

        Parameters:
        data (dict): The dictionary containing the data to be included in the PDF.
        embed_file (str): The path to the file to be embedded in the PDF.
        certificate_name (str): The unique identifier for the certificate file name.
        attach_data (bool): Whether to attach the file to the PDF or not.

        Returns:
        None
        """
        packages = r"""
        %% Language and font encoding
        \usepackage[english]{babel}
        \usepackage{textcomp} %For special symbols
        % To support Hindi symbols
        \usepackage[T1]{fontenc} 
        \usepackage{fontspec}
        \usepackage{polyglossia}
        \setmainlanguage{english} % Continue using english for rest of the document
        \setotherlanguages{hindi} % To use \texthindi to write Hindi in the document
        \newfontfamily\hindifont{Noto Sans Devanagari}[Script=Devanagari] %For Hindi script
        \setmainfont{Arial}% Set Arial as the default font
        \usepackage{longtable} % To split table if it doesn't fit in one page
        \usepackage[scaled]{uarial} % Load the uarial package to use Arial font
        \usepackage[a4paper]{geometry} %To define dimensions of the page
        \usepackage{emptypage}	%To remove header and footer from the last page
        \usepackage{siunitx} %SI units representation
        \usepackage{array}  % for specifying column alignment
        \usepackage{makecell}  % for formatting cells
        \usepackage{xcolor} %To define the color of text
        \usepackage{multirow}%For more flexibility in tables
        \usepackage{multicol}%For more flexibility in tables
        \usepackage{background} %To create a watermark
        \usepackage{tcolorbox} %To use parbox and wrap text
        \usepackage{graphicx} %To include images
        \usepackage{tabularx} %For tables
        \usepackage{lastpage} % For number of pages
        \usepackage{fancyhdr}%header & footer
        \usepackage{setspace} % For setting line spacing
        \usepackage{float} % Aligns the tables to the top for better space utilization

        """


        headers = {
            'calibration': f"""
            \\fancyhead[L]{{
            \\begin{{minipage}}{{13.4cm}}
            \\begin{{spacing}}{{0.6}}
            \\begin{{tabular}}{{>{{\\centering}}m{{2.2cm}} >{{\\centering}}m{{9 cm}} >{{\\centering\\arraybackslash}} m{{2.1 cm}}}}

            \\includegraphics[width=3cm, height=3cm]{{./static/CSIR_logo.png}}		&	\\makecell[bc]{{\\fontsize{{11}}{{12}}\\selectfont \\textbf{{\\texthindi{{सी एस आई आर- राष्ट्रीय भौतिक प्रयोगशाला}}}}\\\\\\fontsize{{11}}{{12}}\\selectfont \\textbf{{CSIR-NATIONAL PHYSICAL LABORATORY}}\\\\\\fontsize{{8}}{{12}}\\selectfont \\texthindi{{(वैज्ञानिक और औद्योगिक अनुसंधान परिषद)}}\\\\\\fontsize{{9}}{{12}}\\selectfont (Council of Scientific and Industrial Research)\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{(राष्ट्रीय मापिकी विज्ञान संस्थान (एनएमआई), सदस्य बीआईपीएम एवं हस्ताक्षरकर्ता सीआईपीएम --एमआरए)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{(National Metrology Institute (NMI), Member BIPM and Signatory CIPM - MRA)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{\\texthindi{{डॉ के एस कृष्णन मार्ग, नई दिल्ली-110012, भारत}}}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{Dr. K. S. Krishnan Marg, New Delhi-110012, INDIA}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{दूरभाष}}\\textbf{{/Phone : 91-11-4560 8441, 8589, 8610, 9447,}}\\texthindi{{फैक्स}}\\textbf{{/Fax : 91-11-4560 8448}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{ई-मेल}}\\textbf{{/E-mail: cfct@nplindia.org,}} \\texthindi{{वेबसाईट}}\\textbf{{/Website: www.nplindia.org}}}}	&	\\hspace{{-0.6cm}}\\raisebox{{0.6cm}}{{\\includegraphics[width=2.35cm, height=2.35cm]{{./static/Logo_NPL_india.png}}}}\\\\
            \\end{{tabular}}
            \\end{{spacing}}
            \\end{{minipage}}%
            \\begin{{minipage}}{{6.2cm}}
            \\setlength{{\\arrayrulewidth}}{{0.8mm}}
            \\begin{{tabular}}{{|>{{\\centering\\arraybackslash}} p{{6.2 cm}}}}
            \\makecell{{\\texthindi{{अंशांकन प्रमाण पत्र}}\\\\\\textbf{{CALLIBRATION CERTIFICATE:}}\\\\{data['device_name']}}}\\\\[1.5ex]
            \\hline
            \\makecell{{\\rule{{0pt}}{{1em}}\\texthindi{{प्रमाण पत्र संख्या}}/Certificate number:\\\\ \\rule{{0pt}}{{1.5em}}{data['certificate_no']}}} \\\\ [1.5ex]
            \\hline
            \\makecell{{\\texthindi{{डी ओ आई संख्या}}/DOI number :\\vspace{{0.15cm}}\\\\ {data['doi_no']} }}\\\\[1.5ex]

            \\end{{tabular}}
            \\end{{minipage}}
            \\begin{{tabular}}{{>{{\\centering}}p{{3.8cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{8.3cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{2.5cm}}!{{\\vrule width 0.8mm}}>{{\\centering\\arraybackslash}}p{{4.9cm}}}}
            \\fullhline
            \\texthindi{{दिनंक}}/\\textbf{{Date}} & \\makecell{{\\texthindi{{अगले अंशांकन हेतु अनुशंसित तिथि}}\\\\\\textbf{{Recommended date for the next calibration}}}} & \\texthindi{{पृष्ठ}}/\\textbf{{Page}} & \\texthindi{{पृष्ठों की संख्या}}/\\textbf{{No of pages}}\\\\
            {data['end_date']}&{data['next_date']}&\\thepage&\\pageref{{LastPage}}\\\\[1.8ex]
            \\fullhline
            \\end{{tabular}}
            }}
            """,
            'testing': f"""
            \\fancyhead[L]{{
            \\begin{{minipage}}{{13.4cm}}
            \\begin{{spacing}}{{0.6}}
            \\begin{{tabular}}{{>{{\\centering}}m{{2.2cm}} >{{\\centering}}m{{9 cm}} >{{\\centering\\arraybackslash}} m{{2.1 cm}}}}

            \\includegraphics[width=3cm, height=3cm]{{./static/CSIR_logo.png}}		&	\\makecell[bc]{{\\fontsize{{11}}{{12}}\\selectfont \\textbf{{\\texthindi{{सी एस आई आर- राष्ट्रीय भौतिक प्रयोगशाला}}}}\\\\\\fontsize{{11}}{{12}}\\selectfont \\textbf{{CSIR-NATIONAL PHYSICAL LABORATORY}}\\\\\\fontsize{{8}}{{12}}\\selectfont \\texthindi{{(वैज्ञानिक और औद्योगिक अनुसंधान परिषद)}}\\\\\\fontsize{{9}}{{12}}\\selectfont (Council of Scientific and Industrial Research)\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{(राष्ट्रीय मापिकी विज्ञान संस्थान (एनएमआई), सदस्य बीआईपीएम एवं हस्ताक्षरकर्ता सीआईपीएम --एमआरए)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{(National Metrology Institute (NMI), Member BIPM and Signatory CIPM - MRA)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{\\texthindi{{डॉ के एस कृष्णन मार्ग, नई दिल्ली-110012, भारत}}}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{Dr. K. S. Krishnan Marg, New Delhi-110012, INDIA}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{दूरभाष}}\\textbf{{/Phone : 91-11-4560 8441, 8589, 8610, 9447,}}\\texthindi{{फैक्स}}\\textbf{{/Fax : 91-11-4560 8448}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{ई-मेल}}\\textbf{{/E-mail: cfct@nplindia.org,}} \\texthindi{{वेबसाईट}}\\textbf{{/Website: www.nplindia.org}}}}	&	\\hspace{{-0.6cm}}\\raisebox{{0.6cm}}{{\\includegraphics[width=2.35cm, height=2.35cm]{{./static/Logo_NPL_india.png}}}}\\\\
            \\end{{tabular}}
            \\end{{spacing}}
            \\end{{minipage}}%
            \\begin{{minipage}}{{6.2cm}}
            \\centering
            \\setlength{{\\arrayrulewidth}}{{0.8mm}}
            \\begin{{tabular}}{{|>{{\\centering\\arraybackslash}}p{{6.2 cm}}}}
            \\makecell{{\\texthindi{{परीक्षण रिपोर्ट}}\\\\\\textbf{{TEST REPORT}}}}\\\\
            \\begin{{minipage}}{{6.2cm}}\\centering{{{data['report_name']}}}\\end{{minipage}}\\\\[0.5cm]
            \\hline
            \\makecell{{\\texthindi{{डी ओ आई संख्या}}/DOI number :\\vspace{{0.15cm}}\\\\ {data['doi_no']} }}\\\\[0.5cm]

            \\end{{tabular}}
            \\end{{minipage}}
            \\begin{{tabular}}{{>{{\\centering}}p{{3.8cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{8.3cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{2.5cm}}!{{\\vrule width 0.8mm}}>{{\\centering\\arraybackslash}}p{{4.9cm}}}}
            \\fullhline
            \\texthindi{{दिनंक}}/\\textbf{{Date}} & \\texthindi{{परीक्षण रिपोर्ट संख्या}}/\\textbf{{Test Report No.}} & \\texthindi{{पृष्ठ}}/\\textbf{{Page}} & \\texthindi{{पृष्ठों की संख्या}}/\\textbf{{No of pages}}\\\\
            {data['end_date']}&{data['report_no']}&\\thepage&\\pageref{{LastPage}}\\\\[1.8ex]
            \\fullhline
            \\end{{tabular}}
            }}
            """
        }

        administrative_data = {
            'calibration': f"""
            \\headsep = 0cm
            \\small
            
            {{
            \\renewcommand{{\\arraystretch}}{{2.4}}
            \\hspace{{0.95cm}}
            \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}  p{{0.5cm}} p{{8cm}}}}
            \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[l]{{Calibrated for}}		&:&	\\parbox[t]{{7.8cm}}{{\\raggedright {data['calibrated_for']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[lt]{{Description and Identification \\\\of Item under Calibration}}  &:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data['description']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Environmental Conditions}} 	& :&	 \\begin{{minipage}}[t]{{7.8cm}}{{\\raggedright {data['env_conditions']}}} \\end{{minipage}}\\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Standard(s) used (with)\\\\ Associated uncertainty}}  &:& \\begin{{minipage}}[t]{{7.8cm}}{{\\raggedright {data['stds_used']}}} \\end{{minipage}}\\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Traceability of standard(s) used}}	&:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data['tracability']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Principle /Methodology of\\\\ calibration and Calibration\\\\ Procedure number}} 	& :&	\\parbox[t]{{7.8cm}}{{\\raggedright {data['procedure']}}} \\\\
            \\end{{tabular}}
            }}
            """,
            'testing': f"""
            \\headsep = 0cm
            \\small
            
            {{
            \\renewcommand{{\\arraystretch}}{{2.4}}
            \\hspace{{0.95cm}}
            \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}  p{{0.5cm}} p{{8cm}}}}
            \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[l]{{Tested for}}		&:&	\\parbox[t]{{7.8cm}}{{\\raggedright {data['tested_for']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[lt]{{Description and Identification \\\\of Sample}}  &:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data['description']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Environmental Conditions}} 	& :&	 \\begin{{minipage}}[t]{{7.8cm}}{{\\raggedright {data['env_conditions']}}} \\end{{minipage}}\\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Standard(s) used (with)\\\\ Associated Uncertainty}}  &:& \\begin{{minipage}}[t]{{7.8cm}}{{\\raggedright {data['stds_used']}}} \\end{{minipage}}\\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Traceability of Standard(s) used}}	&:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data['tracability']}}} \\\\
            \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Principle /Methodology of Test and\\\\Test Procedure number}} 	& :&	\\parbox[t]{{7.8cm}}{{\\raggedright {data['procedure']}}} \\\\
            \\end{{tabular}}
            }}
            """
        }
        
        footers = {
            'calibration': f"""
            \\fancyfoot[C]{{
            \\begin{{minipage}}{{\\textwidth}}
            \\centering
            \\begin{{tabular}}{{ p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} }}
            \\makecell[lb]{{\\texthindi{{आशंकितकर्ता}}\\\\\\textbf{{Calibrated by :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/calibrated_by.jpg}}}}
            & \\makecell[lb]{{\\texthindi{{जाँचकर्ता}}\\\\\\textbf{{Checked by :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/checked_by.jpg}}}}
            & \\makecell[lb]{{\\texthindi{{प्रभारी वैज्ञानिक}}\\\\ \\textbf{{Scientist-in-charge :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/incharge.jpg}}}}\\\\
            \\multicolumn{{2}}{{c}}{{{data['calibrated_by']}}} & \\multicolumn{{2}}{{c}}{{{data['checked_by']}}} & \\multicolumn{{2}}{{c}}{{{data['incharge']}}} \\\\[1.5 ex]
            \\\\
            & & \\makecell[lb]{{\\texthindi{{जारिकर्ता}}\\\\\\textbf{{Issued by :}}}} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/issued_by.jpg}}}} & &\\\\
            & & \\multicolumn{{2}}{{c}}{{{data['issued_by']}}} & & \\\\
            \\end{{tabular}}
            \\end{{minipage}}
            }}
            """,
            'testing': f"""
            \\fancyfoot[C]{{
            \\begin{{minipage}}{{\\textwidth}}
            \\centering
            \\begin{{tabular}}{{ p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} p{{3.5 cm}} }}
            \\makecell[lb]{{\\texthindi{{परीक्षाणकर्ता}}\\\\\\textbf{{Tested by :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/calibrated_by.jpg}}}}
            & \\makecell[lb]{{\\texthindi{{जाँचकर्ता}}\\\\\\textbf{{Checked by :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/checked_by.jpg}}}}
            & \\makecell[lb]{{\\texthindi{{प्रभारी वैज्ञानिक}}\\\\ \\textbf{{Scientist-in-charge :}} }} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/incharge.jpg}}}}\\\\
            \\multicolumn{{2}}{{c}}{{{data['tested_by']}}} & \\multicolumn{{2}}{{c}}{{{data['checked_by']}}} & \\multicolumn{{2}}{{c}}{{{data['incharge']}}} \\\\[1.5 ex]
            \\\\
            & & \\makecell[lb]{{\\texthindi{{जारिकर्ता}}\\\\\\textbf{{Issued by :}}}} & \\parbox[t][0.5cm][l]{{2cm}}{{\\includegraphics[width=1.8cm, height=0.8cm]{{./signatures/issued_by.jpg}}}} & &\\\\
            & & \\multicolumn{{2}}{{c}}{{{data['issued_by']}}} & & \\\\
            \\end{{tabular}}
            \\end{{minipage}}
            }}
            """
        }
        

        Plot_graph=f"""
        \\textbf{{Sample:}} {data['device_name']}\\\\
        \\begin{{center}}
        \\includegraphics[width=0.6\\textwidth]{{./static/graph.png}}\\\\
        \\end{{center}}
        """ if attach_graph else ""

        Measurement_data = f"""
        \\hspace{{0.95cm}}
        \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}}}
        \\stepcounter{{rownum}}\\arabic{{rownum}}. & Result(s): \\\\
        \\end{{tabular}}
        {{
        \\renewcommand{{\\arraystretch}}{{1.3}}
        {data['result_table']}
        }}

        %%%%%%%%%%%%%% Conditional graph plotting %%%%%%%%%%%%%%%%
        {Plot_graph}

        \\hspace{{0.8 cm}}\\begin{{minipage}}[c]{{0.85\\textwidth}}
        {data['result_desc']}
        \\end{{minipage}}\\\\
        %%%%%%%%% Date and Remarks %%%%%%%%%%
        {{
        \\renewcommand{{\\arraystretch}}{{2.4}}
        \\hspace{{0.95cm}}
        \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}} p{{8cm}}}}
        \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	Date(s) for calibration: &	{data['calibration_date']} \\\\
        \\stepcounter{{rownum}}\\arabic{{rownum}}.		&	Remark(s):	&	\\parbox[t]{{8.5cm}}{{\\raggedright {data['remarks']}}}   \\\\
        \\end{{tabular}}
        }}
        """

        last_page = r"""
        \AtEndDocument{ %To keep this at the end of the document
        \newpage %Gives a fresh page
        \thispagestyle{empty} %Clears all the headers
        \newgeometry{top=2cm, bottom=2.4cm, left=1.2cm, right=1.2cm }  % Redefine the margins
        \backgroundsetup{contents={}} % Removes the watermark
        \renewcommand{\seriesdefault}{\bfdefault} % Change the default font style to bold
        \setmainfont{Arial} % Change the default font family to Arial
        \Large %Textsize: 14.4

        \begin{center}\LARGE \texthindi{नोट}\end{center} %Heading of size: 17.28 in the center of the page
        \begin{spacing}{0.8}
        \begin{enumerate}
        \item \texthindi{यह प्रमाण पत्र सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, भारत जारी किया गया है जौ कि विज्ञान एवं प्रौद्योगिकी मंत्रालय, भारत सरकार के अधीन वैज्ञानिक व औद्योगिक अनुसंधान परिषद्‌ की संघटक इकाई है एवम्‌ भारत का राष्ट्रीय मापिकी  संस्थान}(NMI) \texthindi{ भी है ।}
        \item \texthindi{यह प्रमाण पत्र केवल अंशांकन हेतु जमा किएं गए माषिकी हेतु संदर्थित है।}
        \item \texthindi{इस प्रमाण पत्र की प्रतिलिपी, पूर्ण प्रमाण पत्र के अतिरिक्त, तैयार नहीं की जा सकती है, जब तक कि निदेशक, सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, नई दिल्‍ली से अनुमोदित सार के प्रकाशन हेतु लिखित अनुमति प्राप्त नहीं की गयी हो।}
        \item \texthindi{उस प्रमाण पत्र में प्रतिवेदित परीक्षण परिणाम केवल मापन की वर्णित परिस्थलियाँ एवं समय हेतु मान्य है।}
        \end{enumerate}
        \end{spacing}

        \vfill    %Ensures that elements are evenly spaced and spread out
        \centering \includegraphics[width=10cm, height=10cm]{./static/NPL_logo_gray.jpeg} %Includes photo
        \vfill %Ensures that elements are evenly spaced and spread out

        \begin{center}\LARGE NOTE\end{center} %Heading of size: 17.28 in the center of the page
        \begin{spacing}{0.8}
        \begin{enumerate}
        \item This certificate is issued by CSIR-National Physical Laboratory of India (NPLI) which is a constituent unit of the Council of Scientific \& Industrial Research, the Ministry of Science and Technology, Government of India and is also National Metrology Institute (NMI) of India.
        \item This certificate refers only to the particular item (s) submitted for calibration.
        \item This certificate shall not be reproduced, except in full, unless written permission for the publication of an approved abstract has been obtained from the Director, CSIR- National Physical Laboratory. New Delhi.
        \item The calibration results reported in this certificate are valid at the time and under the stated conditions of measurement.
        \end{enumerate}
        \end{spacing}
        }
        """

        page_formatting = f"""
        % Adjust margins
        \\geometry{{
            top=0.9cm,
            bottom=10.7cm,
            left=0.7cm,
            right=0.7cm
        }}

        \\pagestyle{{fancy}} %Defining the page style 
        \\fancyhf{{}}  %Clear the header and footer
        \\newcounter{{rownum}} % Create a new counter to count the number of headings given
        \\renewcommand{{\\headrulewidth}}{{0pt}}	%No line below the header
        \\renewcommand\\footrule{{\\hrule width 19.65cm height 0.5mm}} %To have a line above footer with the specified dimensions

        \\newcommand{{\\fullhline}}{{\\noalign{{\\hrule height 0.8mm}}}} %To have a thick horizontal line for selective columns

        % Set column separation
        \\setlength{{\\tabcolsep}}{{0pt}} %To remove the inter-column space


        % Define watermark
        \\backgroundsetup{{
        scale=1.02,  % Scale the watermark
        opacity=0.05,  % Opacity of the watermark (1 = opaque, 0 = fully transparent)
        angle=0,  % Angle of the watermark
        position=current page.center,  % Position of the watermark
        vshift=-0.6cm,  % Vertical shift of the watermark
        hshift=-0.2mm,  % Horizontal shift of the watermark
        contents={{%
            \\includegraphics[width=10cm,height=10cm]{{./static/Logo_NPL_india.png}}  % Path to your watermark image
        }}
        }}
        """

        embedding = f"\\embedfile{{{embed_file}}}" if attach_data else ""

        latex_template = f"""
        \\DocumentMetadata{{
        pdfversion=1.7,
        pdfstandard=A-3b,
        }}
        \\documentclass[a4paper]{{article}}
        %To support embedding of a file in the PDF/A-3
        \\usepackage{{embedfile}}
        \\embedfilesetup{{     
            filesystem=URL, 
            mimetype=application/octet-stream, % Defined syntax to embed excel files
            afrelationship={{/Data}}, %Relationship of the pdf to the embedded file is data
            stringmethod = escape %Treats an unknown symbol as an escape character
        }}

        %%%%%% Packages included %%%%%%
        {packages}


        %%%%% Page format %%%%%%%
        {page_formatting}


        %%% HEADER %%%
        {headers[doc_type]}

        %%% FOOTER %%%
        {footers[doc_type]}

        \\setlength{{\\headheight}}{{6.9cm}}
        \\setlength{{\\footskip}}{{1.95cm}}


        %%%%%% DOCUMENT BEGINS HERE  %%%%%%%%%%
        \\begin{{document}}
        
        %%%% Administrative Data %%%%%%%
        {administrative_data[doc_type]}

        \\newpage

        %%%%%% Measurement Data %%%%%%%%
        {Measurement_data}


        %%%%%%% LAST PAGE %%%%%%%%%%%
        {last_page}

        {embedding}
        \\end{{document}}
        """

        # Save the LaTeX code to a file
        aux_file = f"{certificate_name}.tex"
        tex_file = f"./pdfs/{aux_file}"
        pdf_file = f"./pdfs/{certificate_name}.pdf"
        
        # write latex file
        with open(tex_file, "w", encoding="utf-8") as file:
            file.write(latex_template)
        print("tex written successfully")

        # convert tex to pdf
        try:
            subprocess.run(["lualatex", tex_file], capture_output=False)
            subprocess.run(["lualatex", tex_file], capture_output=True)
            print("PDF created successfully.")
        except subprocess.CalledProcessError as e:
            print("An error occurred while compiling the LaTeX document:")
            print(e.stderr)

        # Move the generaed PDF file to the pdfs folder
        if os.path.exists(aux_file.replace(".tex", ".pdf")):
            os.replace(aux_file.replace(".tex", ".pdf"), pdf_file)

        # Generate Checksum
        expected_checksum = self.generate_checksum(pdf_file)
        print(f"Generated checksum for {data['certificate_no']}: {expected_checksum}")

        # Store Checksum
        response = add_checksum({
            'checksum': expected_checksum,
            'certificate_no': data['certificate_no'],
            'status':'active'
        })
        print(response)

        #remove extra files generated by LaTeX
        for ext in [".aux", ".log", ".out", ".toc", ".blg", ".bbl"]:
            if os.path.exists(aux_file.replace(".tex", ext)):
                os.remove(aux_file.replace(".tex", ext))
