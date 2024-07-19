from sqlalchemy import create_engine, Column, Text, String, Integer, MetaData, Table, CHAR, delete, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

ind_reg_table = Table(
    'ind_reg', metadata,
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

emp_reg_table = Table(
    'emp_reg', metadata,
    Column('emp_reg_id', Integer, primary_key=True, autoincrement=True),
    Column('f_name', String(100)),
    Column('l_name', String(100)),
    Column('mobile_no', String(20)),
    Column('email', String(255), unique=True),
    Column('emp_id', String(255), unique=True),
    Column('designation', String(50)),
    Column('addr_1', Text),
    Column('password', String(255)),
    Column('signature', LargeBinary),
)

cust_reg_table = Table(
    'cust_reg', metadata,
    Column('cust_reg_id', Integer, primary_key=True, autoincrement=True),
    Column('cust_type', String(40)),
    Column('cust_name', String(100)),
    Column('cust_email', String(255)),
    Column('alt_email', String(255)),
    Column('gst_no', CHAR(15)),
    Column('mobile_no', String(20)),
    Column('landline_no', String(20)),
    Column('cust_addr_1', Text),
    Column('cust_addr_2', Text),
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

def get_org():
    session = SessionLocal()
    try:
        select_stmt = org_reg_table.select()
        result = session.execute(select_stmt).fetchall()
        if result:
            return result
        else:
            return []
    finally:
        session.close()

def check_org_credentials(email: str, password: str) -> bool:
    session = SessionLocal()
    try:
        query = session.query(org_reg_table).filter(
            org_reg_table.c.email == email,
            org_reg_table.c.password == password
        )
        result = session.execute(query).fetchone()
        return result is not None
    finally:
        session.close()

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

def get_ind():
    session = SessionLocal()
    try:
        select_stmt = ind_reg_table.select()
        result = session.execute(select_stmt).fetchall()
        if result:
            return result
        else:
            return []
    finally:
        session.close()

def get_one_ind(ind_reg_id: int):
    session = SessionLocal()
    try:
        select_stmt = ind_reg_table.select().where(ind_reg_table.c.ind_reg_id == ind_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return result._mapping
        else:
            return None
    finally:
        session.close()

def get_one_ind(org_reg_id: int):
    session = SessionLocal()
    try:
        select_stmt = org_reg_table.select().where(org_reg_table.c.org_reg_id == org_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return result._mapping
        else:
            return None
    finally:
        session.close()

def delete_ind(ind_reg_id: int):
    session = SessionLocal()
    try:
        delete_stmt = delete(ind_reg_table).where(ind_reg_table.c.ind_reg_id == ind_reg_id)
        result = session.execute(delete_stmt)
        session.commit()
        return f"Deleted Individual"
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_org(org_reg_id: int):
    session = SessionLocal()
    try:
        delete_stmt = delete(org_reg_table).where(org_reg_table.c.org_reg_id == org_reg_id)
        result = session.execute(delete_stmt)
        session.commit()
        return f"Deleted Organisation"
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

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

def get_emp(emp_reg_id: int):
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

def check_emp_credentials(email: str, password: str):
    session = SessionLocal()
    try:
        query = session.query(emp_reg_table).filter(
            emp_reg_table.c.email == email,
            emp_reg_table.c.password == password
        )
        result = session.execute(query).fetchone()
        if result:
            return {'email': result.email, 'designation': result.designation, 'emp_reg_id': result.emp_reg_id}
        return None
    finally:
        session.close()

def add_new_cust(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = cust_reg_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Customer Registration success'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_cust(cust_reg_id: int):
    session = SessionLocal()
    try:
        select_stmt = cust_reg_table.select().where(cust_reg_table.c.cust_reg_id == cust_reg_id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return result._mapping
        else:
            return None
    finally:
        session.close()

def check_cust_credentials(email: str, password: str) -> dict:
    session = SessionLocal()
    try:
        query = session.query(cust_reg_table).filter(
            cust_reg_table.c.cust_email == email,
            cust_reg_table.c.password == password
        )
        result = session.execute(query).fetchone()
        if result:
            return result._mapping #New method to pass dict?
        else:
            return None
    finally:
        session.close()

checksums_table = Table(
    'checksums', metadata,
    Column('id', Integer, autoincrement=True),
    Column('checksum', CHAR(64),  primary_key=True),
    Column('certificate_no', String(100)),
    Column('status', String(20)),
)

def get_checksum(checksum):
    session = SessionLocal()
    try:
        select_stmt = checksums_table.select().where(checksums_table.c.checksum==checksum)
        result = session.execute(select_stmt).fetchone()
        if result:
            return result
        else:
            return None
    finally:
        session.close()