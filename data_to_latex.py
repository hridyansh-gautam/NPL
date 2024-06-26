<<<<<<< HEAD
import subprocess
import os
import threading
from sqlalchemy import create_engine, Column, Text, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

# Connect to database
db_name = "dcc"
user="postgres"
password="root"
host="localhost"
port="5432"
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Query data template
metadata = MetaData()
certificate_table = Table(
    'certificate', metadata,
    Column('certificateno', String(255), primary_key=True),
    Column('devicename', String(255)),
    Column('enddate', String(10)),
    Column('nextdate', String(10)),
    Column('calibratedfor', Text),
    Column('description', Text),
    Column('envconditions', Text),
    Column('stdsused', Text),
    Column('tracability', Text),
    Column('procedure', Text),
    Column('calibratedby', String(255)),
    Column('checkedby', String(255)),
    Column('incharge', String(255)),
    Column('issuedby', String(255)),
    Column('resulttable', Text),
    Column('resultdesc', Text),
    Column('calibrationdate', String(255)),
    Column('remarks', Text),
    Column('dio_no', String(50))
)

def insert_certificate(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = certificate_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_certificate(certificate_no: str):
    session = SessionLocal()
    try:
        select_stmt = certificate_table.select().where(certificate_table.c.certificateno == certificate_no)
        result = session.execute(select_stmt).fetchone()
        results.append(result)
    finally:
        session.close()

def extract_tables_from_excel(excel_file):
    xls = pd.ExcelFile(excel_file)
    
    tables = []
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        table = []
        header = None
        
        for i, row in df.iterrows():
            if row.isnull().all():
                if table:
                    if header is not None:
                        table_df = pd.DataFrame(table, columns=header)
                        tables.append(table_df.dropna(axis=1, how='all'))
                    table = []
                    header = None 
            else:
                if header is None:
                    header = row.tolist() 
                else:
                    table.append(row.tolist())
        
        if table:
            if header is None:
                header = table.pop(0).tolist() 
            table_df = pd.DataFrame(table, columns=header)
            tables.append(table_df.dropna(axis=1, how='all'))
    
    pg2_tables = ''
    for i, table in enumerate(tables):
        col_count = len(table.columns)
        col_format = ''.join(['|X' for _ in range(col_count)])
        tex = table.to_latex(
            multicolumn=True, 
            header=True, 
            index=False, 
            column_format=col_format + '|',  
            caption=f"This is Table {i + 1}"
        )
        tex = tex.replace('tabular', 'tabularx').replace('\\toprule', '\\hline').replace('\\midrule', '').replace('\\bottomrule', '')
        tex = tex.replace('\\\n', '\\ \\hline\n').replace('\\begin{tabularx}', '\\begin{tabularx}{\\textwidth}')
        pg2_tables += tex
        print(f"Table {i + 1} created.")
    return pg2_tables


def create_pdf(data, stds_used, tabs):
    # LaTeX document
    latex_code = f"""
    \\DocumentMetadata{{
        pdfversion=1.7,
        pdfstandard=A-3b,
    }}
    \\documentclass[a4paper]{{article}}

    %% Language and font encoding
    \\usepackage[english]{{babel}}
    \\usepackage{{textcomp}}
    \\usepackage[T1]{{fontenc}}
    \\usepackage{{fontspec}}
    \\usepackage{{polyglossia}}
    \\setmainlanguage{{english}} % Continue using english for rest of the document
    \\setotherlanguages{{hindi}} % Now can use \\texthindi
    \\newfontfamily\\hindifont{{Noto Sans Devanagari}}[Script=Devanagari]
    \\setmainfont{{Arial}}

    % Load the uarial package to use Arial font
    \\usepackage[scaled]{{uarial}}
    % Set Arial as the default font


    %% Sets page size and margins
    \\usepackage[a4paper]{{geometry}}
    \\usepackage{{emptypage}}
    \\usepackage{{siunitx}}
    \\usepackage{{array}}  % for specifying column alignment
    \\usepackage{{makecell}}  % for formatting cells
    \\usepackage{{longtable}}
    \\usepackage{{booktabs}}
    \\usepackage{{xcolor}}
    \\usepackage{{multirow}}
    \\usepackage{{multicol}}
    \\usepackage{{makecell}}
    \\newcounter{{rownum}} % Create a new counter
    \\usepackage{{wrapfig}}
    \\usepackage{{tcolorbox}}
    \\usepackage{{amsmath}}
    \\usepackage{{graphicx}}
    \\usepackage{{tabularx}}
    \\usepackage{{lastpage}} % For number of pages
    \\usepackage{{fancyhdr}}%header & footer
    \\usepackage{{setspace}} % For setting line spacing


    \\pagestyle{{fancy}}
    % Adjust margins
    \\geometry{{
        top=0.9cm,
        bottom=10.7cm,
        left=0.7cm,
        right=0.7cm
    }}

    \\usepackage{{embedfile}}
    \\embedfilesetup{{     
        filesystem=URL,
        mimetype=application/octet-stream,
        afrelationship={{/Data}},
        stringmethod=escape
    }}
    \\usepackage{{background}}
    %\\pdfgentounicode=1 % So that pdf is machine readable

    \\fancyhf{{}} 

    \\renewcommand{{\\headrulewidth}}{{0pt}}
    \\renewcommand\\footrule{{\\hrule width 19.65cm height 0.5mm}}

    \\newcommand{{\\fullhline}}{{\\noalign{{\\hrule height 0.8mm}}}}

    % Set column separation
    \\setlength{{\\tabcolsep}}{{0pt}}


    % Define watermark
    \\backgroundsetup{{
    scale=1.02,  % Scale the watermark
    opacity=0.1,  % Opacity of the watermark (1 = opaque, 0 = fully transparent)
    angle=0,  % Angle of the watermark
    position=current page.center,  % Position of the watermark
    vshift=-0.6cm,  % Vertical shift of the watermark
    hshift=-0.2mm,  % Horizontal shift of the watermark
    contents={{%
        \\includegraphics[width=10cm,height=10cm]{{Logo_NPL_india.png}}  % Path to your watermark image
    }}
    }}


    %%% HEADER %%%

    \\fancyhead[L]{{
    \\begin{{minipage}}{{13.4cm}}
    \\begin{{spacing}}{{0.6}}
    \\begin{{tabular}}{{>{{\\centering}}m{{2.2cm}} >{{\\centering}}m{{9 cm}} >{{\\centering\\arraybackslash}} m{{2.1 cm}}}}

    \\includegraphics[width=3cm, height=3cm]{{CSIR_logo.png}}		&	\\makecell[bc]{{\\fontsize{{11}}{{12}}\\selectfont \\textbf{{\\texthindi{{सी एस आई आर- राष्ट्रीय भौतिक प्रयोगशाला}}}}\\\\\\fontsize{{11}}{{12}}\\selectfont \\textbf{{CSIR-NATIONAL PHYSICAL LABORATORY}}\\\\\\fontsize{{8}}{{12}}\\selectfont \\texthindi{{(वैज्ञानिक और औद्योगिक अनुसंधान परिषद)}}\\\\\\fontsize{{9}}{{12}}\\selectfont (Council of Scientific and Industrial Research)\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{(राष्ट्रीय मापिकी विज्ञान संस्थान (एनएमआई), सदस्य बीआईपीएम एवं हस्ताक्षरकर्ता सीआईपीएम --एमआरए)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{(National Metrology Institute (NMI), Member BIPM and Signatory CIPM - MRA)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{\\texthindi{{डॉ के एस कृष्णन मार्ग, नई दिल्ली-110012, भारत}}}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{Dr. K. S. Krishnan Marg, New Delhi-110012, INDIA}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{दूरभाष}}\\textbf{{/Phone : 91-11-4560 8441, 8589, 8610, 9447,}}\\texthindi{{फैक्स}}\\textbf{{/Fax : 91-11-4560 8448}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{ई-मेल}}\\textbf{{/E-mail: cfct@nplindia.org,}} \\texthindi{{वेबसाईट}}\\textbf{{/Website: www.nplindia.org}}}}	&	\\hspace{{-0.6cm}}\\raisebox{{0.6cm}}{{\\includegraphics[width=2.35cm, height=2.35cm]{{Logo_NPL_india.png}}}}\\\\
    \\end{{tabular}}
    \\end{{spacing}}
    \\end{{minipage}}%
    \\begin{{minipage}}{{6.2cm}}
    \\begin{{tabular}}{{>{{\\centering\\arraybackslash \\vrule width 0.8mm}} p{{6.2 cm}}}}
    \\makecell{{\\texthindi{{अंशांकन प्रमाण पत्र}}\\\\\\textbf{{CALLIBRATION CERTIFICATE:}}\\\\{data.devicename}}}\\\\[1.5ex]
    \\fullhline
    \\makecell{{\\rule{{0pt}}{{1em}}\\texthindi{{प्रमाण पत्र संख्या}}/Certificate number:\\\\\\rule{{0pt}}{{1.5em}}{data.certificateno}}} \\\\ [1.5ex]
    \\fullhline
    \\makecell{{\\texthindi{{डी ओ आई संख्या}}/DOI number :\\\\ {data.dio_no} }}\\\\[1.5ex]

    \\end{{tabular}}
    \\end{{minipage}}
    \\begin{{tabular}}{{>{{\\centering}}p{{3.8cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{8.3cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{2.5cm}}!{{\\vrule width 0.8mm}}>{{\\centering\\arraybackslash}}p{{4.9cm}}}}
    \\fullhline
    \\texthindi{{दिनंक}}/\\textbf{{Date}} & \\makecell{{\\texthindi{{अगले अंशांकन हेतु अनुशंसित तिथि}}\\\\\\textbf{{Recommended date for the next calibration}}}} & \\texthindi{{पृष्ठ}}/\\textbf{{Page}} & \\texthindi{{पृष्ठों की संख्या}}/\\textbf{{No of pages}}\\\\
    {data.enddate}&{data.nextdate}&\\thepage&\\pageref{{LastPage}}\\\\[1.8ex]
    \\fullhline
    \\end{{tabular}}
    }}


    %%% FOOTER %%%
    \\fancyfoot[C]{{
    \\begin{{minipage}}{{\\textwidth}}
    \\centering
    \\begin{{tabular}}{{ p{{7 cm}}  p{{7 cm}}  p{{7 cm}}}}
    \\texthindi{{आशंकितकर्ता}} & \\texthindi{{जाँचकर्ता}} & \\texthindi{{प्रभारी वैज्ञानिक}} \\\\
    \\textbf{{Caliberated by :}} & \\textbf{{Checked by :}} & \\textbf{{Scientist-in-charge :}}\\multirow{{-1}}{{*}}{{}} \\\\
    \\multicolumn{{1}}{{c}}{{{data.calibratedby}}} & \\multicolumn{{1}}{{c}}{{{data.checkedby}}} & \\multicolumn{{1}}{{c}}{{{data.incharge}}} \\\\[1.5 ex]
    \\\\
    & \\texthindi{{जारिकर्ता}}	 &\\\\
    & \\textbf{{Issued by :}} &\\\\
    & \\multicolumn{{1}}{{c}}{{{data.issuedby}}} & \\\\
    \\end{{tabular}}
    \\end{{minipage}}
    }}

    \\setlength{{\\headheight}}{{6.9cm}}
    \\setlength{{\\footskip}}{{1.95cm}}
    \\begin{{document}}
    \\headsep = 0cm
    \\small
    
    %%%% PAGE 1 %%%%%%%
    {{
    \\renewcommand{{\\arraystretch}}{{2.4}}
    \\hspace{{0.95cm}}
    \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}  p{{0.5cm}} p{{8cm}}}}

    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[l]{{Calibrated for}}		&:&	\\parbox[t]{{7.8cm}}{{\\raggedright {data.calibratedfor}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[lt]{{Description and Identification \\\\of Item under Calibration}}  &:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data.description}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Environmental Conditions}} 	& :&	 \\parbox[t]{{7.8cm}}{{\\raggedright {data.envconditions}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Standard(s) used (with)\\\\ Associated uncertainty}}	&:& 	\\parbox[t]{{7.8cm}}{{\\raggedright  {stds_used}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Traceability of standard(s) used}}	&:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data.tracability}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Principle /Methodology of\\\\ calibration and Calibration\\\\ Procedure number}} 	& :&	\\parbox[t]{{7.8cm}}{{\\raggedright  {data.procedure}}} \\\\
    \\end{{tabular}}
    }}
    \\newpage

    %%%%%% Page 2 %%%%%


    \\stepcounter{{rownum}}\\arabic{{rownum}}. Result(s): \\\\

    {tabs}


    %%%%%%% LAST PAGES %%%%%%%%%%%
    \\AtEndDocument{{
    \\hspace{{0.9cm}}
    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	Date(s) for calibration: \\qquad11/9/2001 \\\\

    \\hspace{{0.9cm}}
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	Remark(s):	\\qquad {data.remarks} \\\\

    \\newpage

    {{%

    \\thispagestyle{{empty}}
    \\clearpage
    \\newgeometry{{top=-12cm, bottom=5cm, left=1.2cm, right=1.2cm}}  % Change margins

    % Change the default font to Arial and make it bold
    \\renewcommand{{\\familydefault}}{{\\sfdefault}}
    \\renewcommand{{\\seriesdefault}}{{\\bfdefault}}
    \\setmainfont{{Arial}}
    \\Large
    \\begin{{center}}\\LARGE \\texthindi{{नोट}}\\end{{center}}
    \\begin{{spacing}}{{0.8}}
    \\begin{{enumerate}}
    \\item \\texthindi{{यह प्रमाण पत्र सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, भारत जारी किया गया है जौ कि विज्ञान एवं प्रौद्योगिकी मंत्रालय, भारत सरकार के अधीन वैज्ञानिक व औद्योगिक अनुसंधान परिषद्‌ की संघटक इकाई है एवम्‌ भारत का राष्ट्रीय मापिकी  संस्थान}}(NMI) \\texthindi{{ भी है ।}}

    \\item \\texthindi{{यह प्रमाण पत्र केवल अंशांकन हेतु जमा किएं गए माषिकी हेतु संदर्थित है।}}

    \\item \\texthindi{{इस प्रमाण पत्र की प्रतिलिपी, पूर्ण प्रमाण पत्र के अतिरिक्त, तैयार नहीं की जा सकती है, जब तक कि निदेशक, सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, नई दिल्‍ली से अनुमोदित सार के प्रकाशन हेतु लिखित अनुमति प्राप्त नहीं की गयी हो।}}

    \\item \\texthindi{{उस प्रमाण पत्र में प्रतिवेदित परीक्षण परिणाम केवल मापन की वर्णित परिस्थलियाँ एवं समय हेतु मान्य है।}}
    \\end{{enumerate}}
    \\end{{spacing}}
    \\centering \\includegraphics[width=9cm, height=9cm]{{NPL_logo_gray.jpeg}}

    \\begin{{center}}\\LARGE NOTE\\end{{center}}
    \\begin{{spacing}}{{0.8}}
    \\begin{{enumerate}}
    \\item This certificate is issued by CSIR-National Physical Laboratory of India (NPLI) which is a constituent unit of the Council of Scientific \\& Industrial Research, the Ministry of Science and Technology, Government of India and is also National Metrology Institute (NMI) of India.
    \\item This certificate refers only to the particular item (s) submitted for calibration.
    \\item This certificate shall not be reproduced, except in full, unless written permission for the publication of an approved abstract has been obtained from the Director, CSIR- National Physical Laboratory. New Delhi.
    \\item The calibration results reported in this certificate are valid at the time and under the stated conditions of measurement.

    \\end{{enumerate}}
    \\end{{spacing}}
    }}}}

    \\embedfile{{user_doc.xlsx}}
    \\end{{document}}
    """

    # Save the LaTeX code to a file
    certificate_id = "001"
    tex_file = f"{certificate_id}.tex"
    with open(tex_file, "w", encoding='utf-8') as file:
        file.write(latex_template)
    print('tex written successfully')
    # convert tex to pdf
    try:
        result = subprocess.run(["lualatex", tex_file], capture_output=True, text=True, check=True)
        result = subprocess.run(["lualatex", tex_file], capture_output=True, text=True, check=True)
        print(result.stdout)
        print("PDF created successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while compiling the LaTeX document:")
        print(e.stderr)

    # remove extra files generated by LaTeX
    for ext in [".aux", ".log", ".out", ".toc", ".tex", ".blg", ".bbl"]:
        if os.path.exists(tex_file.replace(".tex", ext)):
            os.remove(tex_file.replace(".tex", ext))


def data_preprocess(data):
    for key, val in data.items():
        val = val.replace('%', '\\%').replace('#', '\\#').replace('^', '\\^')
        val = val.replace('\u2103', '\\textdegree C').replace('\u03a9', '\\textohm').replace('\u00b1', '\\textpm')
        val = val.replace('\n', ' \\\\\n')
        data[key] = val
    return data

# data
data = {
        "certificateno": "N23070405/D3.03/C-037",
        "devicename": "Defibrillator Analyser",
        "enddate": "12.07.2023",
        "nextdate": "12.07.2024",
        "calibratedfor": "Biomedical Metrology Section National Physical Laboratory, New Delhi, 110012\nCustomer Ref. No. Nil\nDate: 10-07-2023",
        "description": "Defibrillator Analyser\nModel No.: 7000DP, Sr. No.: 3819017\nMake: Fluke Biomedical",
        "envconditions": "Temperature: (25 ± 2) ℃\nRelative Humidity: (50 ± 10)%",
        "stdsused": "1. Digital Storage Oscilloscope (Model No.: TBS 2072; Sr. No.: C020293; Make: Tektronix); \n(-182.8 to -582.4) mV ±1.5 mV (k=2.32) ; \n(215.8 to 2207) mV ± (1.5 to 2.0) mV (k=2.02 to 2.32); \nTime (sec): (19.994 ±1 * 10^-3) μs (k=2)\n\n2. High Voltage Divider (Model No.: VD 15-8.3-A-LB-AL;\nSr. No.: 170313, Make: Ross Engg. Corp.),\n(1000:1) 0.9975 ± 0.1% (k=2.1)\n\n3. Digital Multimeter (Model No. 8846A; Sr.No.: 3641001; Make: Fluke);\n(19.0009 ± 0.0003) Ω (k=2)\n\n4. Defibrillator (Model No.: TEC5621; S. No.: 01273;\nMake: Nihon Kohden);\n(9.5 ± 0.1) J (k=2.16)\n(19.3 ± 0.1) J (k=2.00)\n(48.2 ± 0.2) J (k=2.13)\n(97.1± 0.3) J (k=2.00)\n(146.1 ± 0.5) J (k=2.06)\n(259.5± 0.8) J (k=2.05)",
        "tracability": "The standards used for calibration are traceable to National Standards, which realize the units of quantities according to the International System of Units (SI)",
        "procedure": "Calibration procedure as specified in Sub-Div # 3.03/ Doc3/CP #2",
        "calibratedby": "VINOD KUMAR TANWAR",
        "checkedby": "VED VARUN AGRAWAL",
        "incharge": "Dr. RAJESH",
        "issuedby": "Null",
        "resulttable": "",
        "resultdesc": "The expanded uncertainty in wavelength measurement at NPL. is ±0.5 mm. \n The reported uncertainty is at Coverage factor 1-2, which corresponds to a coverage probability of approximately 95% for a normal distribution.",
        "calibrationdate": "12.07.2023",
        "remarks": ") The measured values of peak wavelength are representation of the nearest reference Standard spectral lines as shown by the Spectrometer at the interval of each 0.1 mm.\n(ii) NPL identification No. of the Spectrometer for wavelength measurement is 402/OPT/202"
    }

def call_thread(target, args):
    t1 = threading.Thread(target=target, args=(args,))
    t1.start()
    t1.join()

results = []

data_to_store = data_preprocess(data)

# insert data
# call_thread(target=insert_certificate, args=data_to_store)

# get data
call_thread(target=get_certificate, args="N23070405/D3.03/C-037")
stds_used = results[0].stdsused.replace('\n \\\\', '\n')
tabs = extract_tables_from_excel('user_doc.xlsx')
=======
import subprocess
import os
import threading
from sqlalchemy import create_engine, Column, Text, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

# Connect to database
db_name = "dcc"
user="postgres"
password="root"
host="localhost"
port="5432"
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Query data template
metadata = MetaData()
certificate_table = Table(
    'certificate', metadata,
    Column('certificateno', String(255), primary_key=True),
    Column('devicename', String(255)),
    Column('enddate', String(10)),
    Column('nextdate', String(10)),
    Column('calibratedfor', Text),
    Column('description', Text),
    Column('envconditions', Text),
    Column('stdsused', Text),
    Column('tracability', Text),
    Column('procedure', Text),
    Column('calibratedby', String(255)),
    Column('checkedby', String(255)),
    Column('incharge', String(255)),
    Column('issuedby', String(255)),
    Column('resulttable', Text),
    Column('resultdesc', Text),
    Column('calibrationdate', String(255)),
    Column('remarks', Text),
    Column('dio_no', String(50))
)

def insert_certificate(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = certificate_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_certificate(certificate_no: str):
    session = SessionLocal()
    try:
        select_stmt = certificate_table.select().where(certificate_table.c.certificateno == certificate_no)
        result = session.execute(select_stmt).fetchone()
        results.append(result)
    finally:
        session.close()

def extract_tables_from_excel(excel_file):
    xls = pd.ExcelFile(excel_file)
    
    tables = []
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        table = []
        header = None
        
        for i, row in df.iterrows():
            if row.isnull().all():
                if table:
                    if header is not None:
                        table_df = pd.DataFrame(table, columns=header)
                        tables.append(table_df.dropna(axis=1, how='all'))
                    table = []
                    header = None 
            else:
                if header is None:
                    header = row.tolist() 
                else:
                    table.append(row.tolist())
        
        if table:
            if header is None:
                header = table.pop(0).tolist() 
            table_df = pd.DataFrame(table, columns=header)
            tables.append(table_df.dropna(axis=1, how='all'))
    
    pg2_tables = ''
    for i, table in enumerate(tables):
        col_count = len(table.columns)
        col_format = ''.join(['|X' for _ in range(col_count)])
        tex = table.to_latex(
            multicolumn=True, 
            header=True, 
            index=False, 
            column_format=col_format + '|',  
            caption=f"This is Table {i + 1}"
        )
        tex = tex.replace('tabular', 'tabularx').replace('\\toprule', '\\hline').replace('\\midrule', '').replace('\\bottomrule', '')
        tex = tex.replace('\\\n', '\\ \\hline\n').replace('\\begin{tabularx}', '\\begin{tabularx}{\\textwidth}')
        pg2_tables += tex
        print(f"Table {i + 1} created.")
    return pg2_tables


def create_pdf(data, stds_used, tabs):
    # LaTeX document
    latex_code = f"""
    \\DocumentMetadata{{
        pdfversion=1.7,
        pdfstandard=A-3b,
    }}
    \\documentclass[a4paper]{{article}}

    %% Language and font encoding
    \\usepackage[english]{{babel}}
    \\usepackage{{textcomp}}
    \\usepackage[T1]{{fontenc}}
    \\usepackage{{fontspec}}
    \\usepackage{{polyglossia}}
    \\setmainlanguage{{english}} % Continue using english for rest of the document
    \\setotherlanguages{{hindi}} % Now can use \\texthindi
    \\newfontfamily\\hindifont{{Noto Sans Devanagari}}[Script=Devanagari]
    \\setmainfont{{Arial}}

    % Load the uarial package to use Arial font
    \\usepackage[scaled]{{uarial}}
    % Set Arial as the default font


    %% Sets page size and margins
    \\usepackage[a4paper]{{geometry}}
    \\usepackage{{emptypage}}
    \\usepackage{{siunitx}}
    \\usepackage{{array}}  % for specifying column alignment
    \\usepackage{{makecell}}  % for formatting cells
    \\usepackage{{longtable}}
    \\usepackage{{booktabs}}
    \\usepackage{{xcolor}}
    \\usepackage{{multirow}}
    \\usepackage{{multicol}}
    \\usepackage{{makecell}}
    \\newcounter{{rownum}} % Create a new counter
    \\usepackage{{wrapfig}}
    \\usepackage{{tcolorbox}}
    \\usepackage{{amsmath}}
    \\usepackage{{graphicx}}
    \\usepackage{{tabularx}}
    \\usepackage{{lastpage}} % For number of pages
    \\usepackage{{fancyhdr}}%header & footer
    \\usepackage{{setspace}} % For setting line spacing


    \\pagestyle{{fancy}}
    % Adjust margins
    \\geometry{{
        top=0.9cm,
        bottom=10.7cm,
        left=0.7cm,
        right=0.7cm
    }}

    \\usepackage{{embedfile}}
    \\embedfilesetup{{     
        filesystem=URL,
        mimetype=application/octet-stream,
        afrelationship={{/Data}},
        stringmethod=escape
    }}
    \\usepackage{{background}}
    %\\pdfgentounicode=1 % So that pdf is machine readable

    \\fancyhf{{}} 

    \\renewcommand{{\\headrulewidth}}{{0pt}}
    \\renewcommand\\footrule{{\\hrule width 19.65cm height 0.5mm}}

    \\newcommand{{\\fullhline}}{{\\noalign{{\\hrule height 0.8mm}}}}

    % Set column separation
    \\setlength{{\\tabcolsep}}{{0pt}}


    % Define watermark
    \\backgroundsetup{{
    scale=1.02,  % Scale the watermark
    opacity=0.1,  % Opacity of the watermark (1 = opaque, 0 = fully transparent)
    angle=0,  % Angle of the watermark
    position=current page.center,  % Position of the watermark
    vshift=-0.6cm,  % Vertical shift of the watermark
    hshift=-0.2mm,  % Horizontal shift of the watermark
    contents={{%
        \\includegraphics[width=10cm,height=10cm]{{Logo_NPL_india.png}}  % Path to your watermark image
    }}
    }}


    %%% HEADER %%%

    \\fancyhead[L]{{
    \\begin{{minipage}}{{13.4cm}}
    \\begin{{spacing}}{{0.6}}
    \\begin{{tabular}}{{>{{\\centering}}m{{2.2cm}} >{{\\centering}}m{{9 cm}} >{{\\centering\\arraybackslash}} m{{2.1 cm}}}}

    \\includegraphics[width=3cm, height=3cm]{{CSIR_logo.png}}		&	\\makecell[bc]{{\\fontsize{{11}}{{12}}\\selectfont \\textbf{{\\texthindi{{सी एस आई आर- राष्ट्रीय भौतिक प्रयोगशाला}}}}\\\\\\fontsize{{11}}{{12}}\\selectfont \\textbf{{CSIR-NATIONAL PHYSICAL LABORATORY}}\\\\\\fontsize{{8}}{{12}}\\selectfont \\texthindi{{(वैज्ञानिक और औद्योगिक अनुसंधान परिषद)}}\\\\\\fontsize{{9}}{{12}}\\selectfont (Council of Scientific and Industrial Research)\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{(राष्ट्रीय मापिकी विज्ञान संस्थान (एनएमआई), सदस्य बीआईपीएम एवं हस्ताक्षरकर्ता सीआईपीएम --एमआरए)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{(National Metrology Institute (NMI), Member BIPM and Signatory CIPM - MRA)}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{\\texthindi{{डॉ के एस कृष्णन मार्ग, नई दिल्ली-110012, भारत}}}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\textbf{{Dr. K. S. Krishnan Marg, New Delhi-110012, INDIA}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{दूरभाष}}\\textbf{{/Phone : 91-11-4560 8441, 8589, 8610, 9447,}}\\texthindi{{फैक्स}}\\textbf{{/Fax : 91-11-4560 8448}}\\\\\\fontsize{{6}}{{12}}\\selectfont \\texthindi{{ई-मेल}}\\textbf{{/E-mail: cfct@nplindia.org,}} \\texthindi{{वेबसाईट}}\\textbf{{/Website: www.nplindia.org}}}}	&	\\hspace{{-0.6cm}}\\raisebox{{0.6cm}}{{\\includegraphics[width=2.35cm, height=2.35cm]{{Logo_NPL_india.png}}}}\\\\
    \\end{{tabular}}
    \\end{{spacing}}
    \\end{{minipage}}%
    \\begin{{minipage}}{{6.2cm}}
    \\begin{{tabular}}{{>{{\\centering\\arraybackslash \\vrule width 0.8mm}} p{{6.2 cm}}}}
    \\makecell{{\\texthindi{{अंशांकन प्रमाण पत्र}}\\\\\\textbf{{CALLIBRATION CERTIFICATE:}}\\\\{data.devicename}}}\\\\[1.5ex]
    \\fullhline
    \\makecell{{\\rule{{0pt}}{{1em}}\\texthindi{{प्रमाण पत्र संख्या}}/Certificate number:\\\\\\rule{{0pt}}{{1.5em}}{data.certificateno}}} \\\\ [1.5ex]
    \\fullhline
    \\makecell{{\\texthindi{{डी ओ आई संख्या}}/DOI number :\\\\ {data.dio_no} }}\\\\[1.5ex]

    \\end{{tabular}}
    \\end{{minipage}}
    \\begin{{tabular}}{{>{{\\centering}}p{{3.8cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{8.3cm}}!{{\\vrule width 0.8mm}}>{{\\centering}}p{{2.5cm}}!{{\\vrule width 0.8mm}}>{{\\centering\\arraybackslash}}p{{4.9cm}}}}
    \\fullhline
    \\texthindi{{दिनंक}}/\\textbf{{Date}} & \\makecell{{\\texthindi{{अगले अंशांकन हेतु अनुशंसित तिथि}}\\\\\\textbf{{Recommended date for the next calibration}}}} & \\texthindi{{पृष्ठ}}/\\textbf{{Page}} & \\texthindi{{पृष्ठों की संख्या}}/\\textbf{{No of pages}}\\\\
    {data.enddate}&{data.nextdate}&\\thepage&\\pageref{{LastPage}}\\\\[1.8ex]
    \\fullhline
    \\end{{tabular}}
    }}


    %%% FOOTER %%%
    \\fancyfoot[C]{{
    \\begin{{minipage}}{{\\textwidth}}
    \\centering
    \\begin{{tabular}}{{ p{{7 cm}}  p{{7 cm}}  p{{7 cm}}}}
    \\texthindi{{आशंकितकर्ता}} & \\texthindi{{जाँचकर्ता}} & \\texthindi{{प्रभारी वैज्ञानिक}} \\\\
    \\textbf{{Caliberated by :}} & \\textbf{{Checked by :}} & \\textbf{{Scientist-in-charge :}}\\multirow{{-1}}{{*}}{{}} \\\\
    \\multicolumn{{1}}{{c}}{{{data.calibratedby}}} & \\multicolumn{{1}}{{c}}{{{data.checkedby}}} & \\multicolumn{{1}}{{c}}{{{data.incharge}}} \\\\[1.5 ex]
    \\\\
    & \\texthindi{{जारिकर्ता}}	 &\\\\
    & \\textbf{{Issued by :}} &\\\\
    & \\multicolumn{{1}}{{c}}{{{data.issuedby}}} & \\\\
    \\end{{tabular}}
    \\end{{minipage}}
    }}

    \\setlength{{\\headheight}}{{6.9cm}}
    \\setlength{{\\footskip}}{{1.95cm}}
    \\begin{{document}}
    \\headsep = 0cm
    \\small
    
    %%%% PAGE 1 %%%%%%%
    {{
    \\renewcommand{{\\arraystretch}}{{2.4}}
    \\hspace{{0.95cm}}
    \\begin{{tabular}}{{p{{1cm}} p{{6.74cm}}  p{{0.5cm}} p{{8cm}}}}

    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[l]{{Calibrated for}}		&:&	\\parbox[t]{{7.8cm}}{{\\raggedright {data.calibratedfor}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	&	\\makecell[lt]{{Description and Identification \\\\of Item under Calibration}}  &:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data.description}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Environmental Conditions}} 	& :&	 \\parbox[t]{{7.8cm}}{{\\raggedright {data.envconditions}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Standard(s) used (with)\\\\ Associated uncertainty}}	&:& 	\\parbox[t]{{7.8cm}}{{\\raggedright  {stds_used}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Traceability of standard(s) used}}	&:&	\\parbox[t]{{7.8cm}}{{ \\raggedright {data.tracability}}} \\\\
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	&	\\makecell[lt]{{Principle /Methodology of\\\\ calibration and Calibration\\\\ Procedure number}} 	& :&	\\parbox[t]{{7.8cm}}{{\\raggedright  {data.procedure}}} \\\\
    \\end{{tabular}}
    }}
    \\newpage

    %%%%%% Page 2 %%%%%


    \\stepcounter{{rownum}}\\arabic{{rownum}}. Result(s): \\\\

    {tabs}


    %%%%%%% LAST PAGES %%%%%%%%%%%
    \\AtEndDocument{{
    \\hspace{{0.9cm}}
    \\stepcounter{{rownum}}\\arabic{{rownum}}. 	Date(s) for calibration: \\qquad11/9/2001 \\\\

    \\hspace{{0.9cm}}
    \\stepcounter{{rownum}}\\arabic{{rownum}}.	Remark(s):	\\qquad {data.remarks} \\\\

    \\newpage

    {{%

    \\thispagestyle{{empty}}
    \\clearpage
    \\newgeometry{{top=-12cm, bottom=5cm, left=1.2cm, right=1.2cm}}  % Change margins

    % Change the default font to Arial and make it bold
    \\renewcommand{{\\familydefault}}{{\\sfdefault}}
    \\renewcommand{{\\seriesdefault}}{{\\bfdefault}}
    \\setmainfont{{Arial}}
    \\Large
    \\begin{{center}}\\LARGE \\texthindi{{नोट}}\\end{{center}}
    \\begin{{spacing}}{{0.8}}
    \\begin{{enumerate}}
    \\item \\texthindi{{यह प्रमाण पत्र सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, भारत जारी किया गया है जौ कि विज्ञान एवं प्रौद्योगिकी मंत्रालय, भारत सरकार के अधीन वैज्ञानिक व औद्योगिक अनुसंधान परिषद्‌ की संघटक इकाई है एवम्‌ भारत का राष्ट्रीय मापिकी  संस्थान}}(NMI) \\texthindi{{ भी है ।}}

    \\item \\texthindi{{यह प्रमाण पत्र केवल अंशांकन हेतु जमा किएं गए माषिकी हेतु संदर्थित है।}}

    \\item \\texthindi{{इस प्रमाण पत्र की प्रतिलिपी, पूर्ण प्रमाण पत्र के अतिरिक्त, तैयार नहीं की जा सकती है, जब तक कि निदेशक, सी एस आई आर-राष्ट्रीय भौतिक प्रयोगशाला, नई दिल्‍ली से अनुमोदित सार के प्रकाशन हेतु लिखित अनुमति प्राप्त नहीं की गयी हो।}}

    \\item \\texthindi{{उस प्रमाण पत्र में प्रतिवेदित परीक्षण परिणाम केवल मापन की वर्णित परिस्थलियाँ एवं समय हेतु मान्य है।}}
    \\end{{enumerate}}
    \\end{{spacing}}
    \\centering \\includegraphics[width=9cm, height=9cm]{{NPL_logo_gray.jpeg}}

    \\begin{{center}}\\LARGE NOTE\\end{{center}}
    \\begin{{spacing}}{{0.8}}
    \\begin{{enumerate}}
    \\item This certificate is issued by CSIR-National Physical Laboratory of India (NPLI) which is a constituent unit of the Council of Scientific \\& Industrial Research, the Ministry of Science and Technology, Government of India and is also National Metrology Institute (NMI) of India.
    \\item This certificate refers only to the particular item (s) submitted for calibration.
    \\item This certificate shall not be reproduced, except in full, unless written permission for the publication of an approved abstract has been obtained from the Director, CSIR- National Physical Laboratory. New Delhi.
    \\item The calibration results reported in this certificate are valid at the time and under the stated conditions of measurement.

    \\end{{enumerate}}
    \\end{{spacing}}
    }}}}

    \\embedfile{{user_doc.xlsx}}
    \\end{{document}}
    """

    # Save the LaTeX code to a file
    certificate_id = "001"
    tex_file = f"{certificate_id}.tex"
    with open(tex_file, "w", encoding='utf-8') as file:
        file.write(latex_template)
    print('tex written successfully')
    # convert tex to pdf
    try:
        result = subprocess.run(["lualatex", tex_file], capture_output=True, text=True, check=True)
        result = subprocess.run(["lualatex", tex_file], capture_output=True, text=True, check=True)
        print(result.stdout)
        print("PDF created successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while compiling the LaTeX document:")
        print(e.stderr)

    # remove extra files generated by LaTeX
    for ext in [".aux", ".log", ".out", ".toc", ".tex", ".blg", ".bbl"]:
        if os.path.exists(tex_file.replace(".tex", ext)):
            os.remove(tex_file.replace(".tex", ext))


def data_preprocess(data):
    for key, val in data.items():
        val = val.replace('%', '\\%').replace('#', '\\#').replace('^', '\\^')
        val = val.replace('\u2103', '\\textdegree C').replace('\u03a9', '\\textohm').replace('\u00b1', '\\textpm')
        val = val.replace('\n', ' \\\\\n')
        data[key] = val
    return data

# data
data = {
        "certificateno": "N23070405/D3.03/C-037",
        "devicename": "Defibrillator Analyser",
        "enddate": "12.07.2023",
        "nextdate": "12.07.2024",
        "calibratedfor": "Biomedical Metrology Section National Physical Laboratory, New Delhi, 110012\nCustomer Ref. No. Nil\nDate: 10-07-2023",
        "description": "Defibrillator Analyser\nModel No.: 7000DP, Sr. No.: 3819017\nMake: Fluke Biomedical",
        "envconditions": "Temperature: (25 ± 2) ℃\nRelative Humidity: (50 ± 10)%",
        "stdsused": "1. Digital Storage Oscilloscope (Model No.: TBS 2072; Sr. No.: C020293; Make: Tektronix); \n(-182.8 to -582.4) mV ±1.5 mV (k=2.32) ; \n(215.8 to 2207) mV ± (1.5 to 2.0) mV (k=2.02 to 2.32); \nTime (sec): (19.994 ±1 * 10^-3) μs (k=2)\n\n2. High Voltage Divider (Model No.: VD 15-8.3-A-LB-AL;\nSr. No.: 170313, Make: Ross Engg. Corp.),\n(1000:1) 0.9975 ± 0.1% (k=2.1)\n\n3. Digital Multimeter (Model No. 8846A; Sr.No.: 3641001; Make: Fluke);\n(19.0009 ± 0.0003) Ω (k=2)\n\n4. Defibrillator (Model No.: TEC5621; S. No.: 01273;\nMake: Nihon Kohden);\n(9.5 ± 0.1) J (k=2.16)\n(19.3 ± 0.1) J (k=2.00)\n(48.2 ± 0.2) J (k=2.13)\n(97.1± 0.3) J (k=2.00)\n(146.1 ± 0.5) J (k=2.06)\n(259.5± 0.8) J (k=2.05)",
        "tracability": "The standards used for calibration are traceable to National Standards, which realize the units of quantities according to the International System of Units (SI)",
        "procedure": "Calibration procedure as specified in Sub-Div # 3.03/ Doc3/CP #2",
        "calibratedby": "VINOD KUMAR TANWAR",
        "checkedby": "VED VARUN AGRAWAL",
        "incharge": "Dr. RAJESH",
        "issuedby": "Null",
        "resulttable": "",
        "resultdesc": "The expanded uncertainty in wavelength measurement at NPL. is ±0.5 mm. \n The reported uncertainty is at Coverage factor 1-2, which corresponds to a coverage probability of approximately 95% for a normal distribution.",
        "calibrationdate": "12.07.2023",
        "remarks": ") The measured values of peak wavelength are representation of the nearest reference Standard spectral lines as shown by the Spectrometer at the interval of each 0.1 mm.\n(ii) NPL identification No. of the Spectrometer for wavelength measurement is 402/OPT/202"
    }

def call_thread(target, args):
    t1 = threading.Thread(target=target, args=(args,))
    t1.start()
    t1.join()

results = []

data_to_store = data_preprocess(data)

# insert data
# call_thread(target=insert_certificate, args=data_to_store)

# get data
call_thread(target=get_certificate, args="N23070405/D3.03/C-037")
stds_used = results[0].stdsused.replace('\n \\\\', '\n')
tabs = extract_tables_from_excel('user_doc.xlsx')
>>>>>>> 00610d0cc822e210479e1d695d24fb5517bd713d
create_pdf(results[0], stds_used, tabs)