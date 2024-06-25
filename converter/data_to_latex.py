import subprocess
import os
import threading
from sqlalchemy import create_engine, Column, Text, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
from generate_pdf import Template

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
        col_format = ''.join(['|X' for _ in range(1,col_count)])
        tex = table.to_latex(
            multicolumn=True, 
            header=True, 
            index=False, 
            column_format='|>{\centering}p{1cm}' + col_format + '|',  
            caption=f"This is Table {i + 1}"
        )
        tex = tex.replace('tabular', 'tabularx').replace('\\toprule', '\\hline').replace('\\midrule', '').replace('\\bottomrule', '')
        tex = tex.replace('\\\n', '\\ \\hline\n').replace('\\begin{tabularx}', '\\begin{tabularx}{\\textwidth}')
        pg2_tables += tex
        print(f"Table {i + 1} created.")
    return pg2_tables

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
# stds_used = results[0].stdsused.replace('\n \\\\', '\n')
tabs = extract_tables_from_excel('user_doc.xlsx')
print(tabs)
template = Template()
template.create_pdf(results[0], tabs)