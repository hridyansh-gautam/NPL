import subprocess
import os
import hashlib


def generate_checksum(filename):
  # Open the file in binary read mode
  with open(filename, 'rb') as file:
    # Create a SHA-256 hash object
    hasher = hashlib.sha256()
    # Read the file content in chunks and update the hash
    for chunk in iter(lambda: file.read(), b''):
      hasher.update(chunk)
    # Return the checksum in hexadecimal format
    return hasher.hexdigest()

def verify_checksum(filename, expected_checksum):
    actual_checksum = generate_checksum(filename)
    return actual_checksum == expected_checksum


def create_pdf(data, embed_file, certificate_id):
    # LaTeX document

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
    \usepackage{makecell} %For more flexibility in tables
    \usepackage{background} %To create a watermark
    \usepackage{tcolorbox} %To use parbox and wrap text
    \usepackage{graphicx} %To include images
    \usepackage{tabularx} %For tables
    \usepackage{lastpage} % For number of pages
    \usepackage{fancyhdr}%header & footer
    \usepackage{setspace} % For setting line spacing
    \usepackage{float} % Aligns the tables to the top for better space utilization
    \usepackage{ifthen} % For conditional embedding of data
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
    \\newcommand{{\\embedCondition}}{{yes}} % Change to "no" if you don't want to embed the file
    
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

    header = f"""
    \\fancyhead[L]{{
    \\begin{{minipage}}{{13.4cm}}
    \\begin{{spacing}}{{0.6}}
    \\begin{{tabular}}{{>{{\\centering}}m{{2.2cm}} >{{\\centering}}m{{9 cm}} >{{\\centering\\arraybackslash}} m{{2.1 cm}}}}

    \\includegraphics[width=3cm, height=3cm]{{./static/CSIR_logo.png}}		&	\\makecell[bc]{{\\fontsize{{11}}{{12}}\\selectfont \\textbf{{\\texthindi{{सी एस आई आर- राष्ट्रीय भौतिक प्रयोगशाला}}}}\\\\\\fontsize{{11}}{{12}}\\selectfont \\textbf{{CSIR-NATIONAL PHYSICAL LABORATORY}}\\\\\\fontsize{{8}}{{12}}\\selectfont \\texthindi{{(वैज्ञानिक और औद्योगिक अनुसंधान परिषद)}}\\\\\\fontsize{{9}}{{12}}\\selectfont (Council of Scientific and Industrial Research)\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{(राष्ट्रीय मापिकी विज्ञान संस्थान (एनएमआई), सदस्य बीआईपीएम एवं हस्ताक्षरकर्ता सीआईपीएम --एमआरए)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{(National Metrology Institute (NMI), Member BIPM and Signatory CIPM - MRA)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{\\texthindi{{डॉ के एस कृष्णन मार्ग, नई दिल्ली-110012, भारत}}}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{Dr. K. S. Krishnan Marg, New Delhi-110012, INDIA}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{दूरभाष}}\\textbf{{/Phone : 91-11-4560 8441, 8589, 8610, 9447,}}\\texthindi{{फैक्स}}\\textbf{{/Fax : 91-11-4560 8448}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{ई-मेल}}\\textbf{{/E-mail: cfct@nplindia.org,}} \\texthindi{{वेबसाईट}}\\textbf{{/Website: www.nplindia.org}}}}	&	\\hspace{{-0.6cm}}\\raisebox{{0.6cm}}{{\\includegraphics[width=2.35cm, height=2.35cm]{{./static/Logo_NPL_india.png}}}}\\\\
    \\end{{tabular}}
    \\end{{spacing}}
    \\end{{minipage}}%
    \\begin{{minipage}}{{6.2cm}}
    \\begin{{tabular}}{{>{{\\centering\\arraybackslash \\vrule width 0.8mm}} p{{6.2 cm}}}}
    \\makecell{{\\texthindi{{अंशांकन प्रमाण पत्र}}\\\\\\textbf{{CALLIBRATION CERTIFICATE:}}\\\\{data['device_name']}}}\\\\[1.5ex]
    \\fullhline
    \\makecell{{\\rule{{0pt}}{{1em}}\\texthindi{{प्रमाण पत्र संख्या}}/Certificate number:\\\\ \\rule{{0pt}}{{1.5em}}{data['certificate_no']}}} \\\\ [1.5ex]
    \\fullhline
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
    """
    

    footer = f"""
    \\fancyfoot[C]{{
    \\begin{{minipage}}{{\\textwidth}}
    \\centering
    \\begin{{tabular}}{{ p{{7 cm}}  p{{7 cm}}  p{{7 cm}}}}
    \\texthindi{{आशंकितकर्ता}} & \\texthindi{{जाँचकर्ता}} & \\texthindi{{प्रभारी वैज्ञानिक}} \\\\
    \\textbf{{Caliberated by :}} & \\textbf{{Checked by :}} & \\textbf{{Scientist-in-charge :}}\\multirow{{-1}}{{*}}{{}} \\\\
    \\multicolumn{{1}}{{c}}{{{data['calibrated_by']}}} & \\multicolumn{{1}}{{c}}{{{data['checked_by']}}} & \\multicolumn{{1}}{{c}}{{{data['incharge']}}} \\\\[1.5 ex]
    \\\\
    & \\texthindi{{जारिकर्ता}}	 &\\\\
    & \\textbf{{Issued by :}} &\\\\
    & \\multicolumn{{1}}{{c}}{{{data['issued_by']}}} & \\\\
    \\end{{tabular}}
    \\end{{minipage}}
    }}
    """


    administrative_data = f"""
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
    """


    Measurement_data = f"""
    \\hspace{{0.95cm}}
    \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}}}
    \\stepcounter{{rownum}}\\arabic{{rownum}}. & Result(s): \\\\
    \\end{{tabular}}
    {{
    \\renewcommand{{\\arraystretch}}{{1.3}}
    {data['result_table']}
    }}
    
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
        stringmethod=escape % Treats an unknown symbol as an escape character
    }}

    %%%%%% Packages included %%%%%%
    {packages}


    %%%%% Page format %%%%%%%
    {page_formatting}


    %%% HEADER %%%
    {header}

    %%% FOOTER %%%
    {footer}

    \\setlength{{\\headheight}}{{6.9cm}}
    \\setlength{{\\footskip}}{{1.95cm}}
    %%%%%% DOCUMENT BEGINS HERE  %%%%%%%%%%
    \\begin{{document}}
    
    %%%% Administrative Data %%%%%%%
    {administrative_data}

    \\newpage

    %%%%%% Measurement Data %%%%%%%%
   {Measurement_data}


    %%%%%%% LAST PAGE %%%%%%%%%%%
    {last_page}
    \\ifthenelse{{\\equal{{\\embedCondition}}{{yes}}}}{{
            \\embedfile{{{embed_file}}}
    }}   {{
        % Do nothing if the condition is not met
    }}
    \\end{{document}}
    """

    # Save the LaTeX code to a file
    aux_file = f"{certificate_id}.tex"
    tex_file = f"./pdfs/{certificate_id}.tex"
    pdf_file = f"./pdfs/{certificate_id}.pdf"
    with open(tex_file, "w", encoding='utf-8') as file:
        file.write(latex_template)
    print('tex written successfully')
    # convert tex to pdf
    try:
        subprocess.run(["lualatex", tex_file])
        #, capture_output=True
        subprocess.run(["lualatex", tex_file])
        print("PDF created successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while compiling the LaTeX document:")
        print(e.stderr)

    # Move the generaed PDF file to the pdfs folder
    if os.path.exists(aux_file.replace(".tex", ".pdf")):
        os.replace(aux_file.replace(".tex", ".pdf"), pdf_file)
    
    # remove extra files generated by LaTeX
    for ext in [".aux", ".log", ".out", ".toc", ".blg", ".bbl"]:
        if os.path.exists(aux_file.replace(".tex", ext)):
            os.remove(aux_file.replace(".tex", ext))
