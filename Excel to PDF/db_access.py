from sqlalchemy import create_engine, Column, Text, String, MetaData, Table, Integer, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict

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
    Column('cert_id', Integer, autoincrement=True),
    Column('cert_no', String(255), primary_key=True),
    Column('device_name', String(255)),
    Column('end_date', String(12)),
    Column('next_date', String(12)),
    Column('calibrated_for', Text),
    Column('description', Text),
    Column('env_conditions', Text),
    Column('stds_used', Text),
    Column('tracability', Text),
    Column('procedure', Text),
    Column('calibrated_by', String(255)),
    Column('checked_by', String(255)),
    Column('incharge', String(255)),
    Column('issued_by', String(255)),
    Column('result_table', Text),
    Column('result_desc', Text),
    Column('calibration_date', String(255)),
    Column('dio_no', String(50)),
    Column('remarks', Text),
    Column('checksum', String(255))
)

def add_new_org(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = certificate_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'New record added successfully'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_org(org_reg_id: str):
    session = SessionLocal()
    try:
        select_stmt = certificate_table.select().where(certificate_table.c.org_reg_id == org_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()

# def check_org_credentials(email: str, password: str) -> bool:
#     session = SessionLocal()
#     try:
#         # Query to check if the given email and password exist in the table
#         query = session.query(certificate_table).filter(
#             certificate_table.c.email == email,
#             certificate_table.c.password == password
#         )
#         # Execute the query and check if any row matches
#         result = session.execute(query).fetchone()
#         return result is not None
#     finally:
#         session.close()
