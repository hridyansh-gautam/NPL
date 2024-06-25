from sqlalchemy import create_engine, Column, Text, String, MetaData, Table, Integer, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict

# Connect to database
db_name = "npl"
user="postgres"
password="clearpointdivine"
host="localhost"
port="5432"
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Query data template
metadata = MetaData()
org_reg_table = Table(
    'org_reg', metadata,
    Column('org_reg_id', Integer, primary_key=True, autoincrement=True),
    Column('org_type', String(40)),  
    Column('org_name', String(255)),  
    Column('gst_no', String(20)),  
    Column('phone', String(20)),  
    Column('landline', String(20)), 
    Column('email', String(255), unique=True),  
    Column('alt_email', String(255), unique=True),  
    Column('addr_1', Text),
    Column('country', String(100)),  
    Column('state', String(100)),  
    Column('city', String(100)),  
    Column('pincode', String(15)),  
    Column('password', String(255))  
)

def add_new_org(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = org_reg_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Organisation Registration success'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_org(org_reg_id: str):
    session = SessionLocal()
    try:
        select_stmt = org_reg_table.select().where(org_reg_table.c.org_reg_id == org_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()

def check_org_credentials(email: str, password: str) -> bool:
    session = SessionLocal()
    try:
        # Query to check if the given email and password exist in the table
        query = session.query(org_reg_table).filter(
            org_reg_table.c.email == email,
            org_reg_table.c.password == password
        )
        # Execute the query and check if any row matches
        result = session.execute(query).fetchone()
        return result is not None
    finally:
        session.close()

metadata2 = MetaData()
ind_reg_table = Table(
    'ind_reg', metadata2,
    Column('ind_reg_id', Integer, primary_key=True, autoincrement=True),
    Column('f_name', String(100)),  
    Column('l_name', String(100)),  
    Column('mobile_no', String(20)),  
    Column('email', String(255), unique=True),  
    Column('alt_email', String(255), unique=True),  
    Column('addr_1', Text),
    Column('addr_2', Text),
    Column('country', String(100)),  
    Column('state', String(100)),  
    Column('city', String(100)),  
    Column('pincode', String(15)),  
    Column('password', String(255))  
)

def add_new_ind(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = ind_reg_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Individual Registration success'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_ind(ind_reg_id: str):
    session = SessionLocal()
    try:
        select_stmt = ind_reg_table.select().where(ind_reg_table.c.ind_reg_id == ind_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()


metadata3 = MetaData()
emp_reg_table = Table(
    'emp_reg', metadata3,
    Column('emp_reg_id', Integer, primary_key=True, autoincrement=True),
    Column('f_name', String(100)),  
    Column('l_name', String(100)),  
    Column('mobile_no', String(20)),  
    Column('email', String(255), unique=True),  
    Column('emp_id', String(255), unique=True),    
    Column('designation', String(50)),  
    Column('addr_1', Text),
    Column('password', String(255))  
)

def add_new_emp(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = emp_reg_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Employee Registration success'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        

def get_emp(emp_reg_id: str):
    session = SessionLocal()
    try:
        select_stmt = emp_reg_table.select().where(emp_reg_table.c.emp_reg_id == emp_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()