from sqlalchemy import create_engine, Column, Text, String, Integer, MetaData, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

meteorological_classification = Table(
    'meteorological_classification', metadata,
    Column('id', Integer, autoincrement=True),
    Column('service_code', String(50), primary_key=True),
    Column('service_types', String(255)),
    Column('service_name', String(255)),
)

meteorological_services = Table(
    'meteorological_services', metadata,
    Column('si_no', Integer, primary_key=True, autoincrement=True),
    Column('service_code', String(255), ForeignKey('meteorological_classification.service_code'), primary_key=True),
    Column('parameter', String(255)),
    Column('item_type_group', String(255)),
    Column('item_name', String(255)),
    Column('alias_name', String(255)),
    Column('range', String(255)),
    Column('calibration_parameters', String(255)),
    Column('no_of_points_for_calibration_procedure_no', String(255)),
    Column('limitation_condition', String(255)),
)

meteorological_services_charges = Table(
    'meteorological_services_charges', metadata,
    Column('si_no', Integer, ForeignKey('meteorological_services.si_no'), primary_key=True),
    Column('service_code', String(255), ForeignKey('meteorological_services.service_code'), primary_key=True),
    Column('charges_per_item_rs', String(255)),
    Column('additional_charges_rs', String(255)),
    Column('description_for_additional_charges', Text),
    Column('remarks_if_any', Text),
    Column('normal', String(255)),
    Column('tatkal', String(255)),
    Column('edc', String(255)),
)

def add_new_classification(data: dict):
    session = SessionLocal()
    try:
        service = MeteorologicalClassification(**data)
        session.add(service)
        session.commit()
        return 'Classification successfully added'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_new_service(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = meteorological_services.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Service details successfully added'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_new_service_charges(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = meteorological_services_charges.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Service charges successfully added'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_classification():
    session = SessionLocal()
    try:
        select_stmt = meteorological_classification.select().distinct()
        classifications = session.execute(select_stmt).fetchall()
        if classifications:
            return classifications
        else:
            return None
    finally:
        session.close()

def row_to_dict(row):
    return {key: getattr(row, key) for key in row._mapping.keys()}
    
def get_services(filters):
    session = SessionLocal()
    try:
        # Start with a base query
        select_stmt = meteorological_services.select()
        
        # Iterate over the dictionary and apply filters for non-empty values
        for column_name, value in filters.items():
            if value:  # Check if the value is not empty
                column = getattr(meteorological_services.c, column_name)
                if value == 'null':
                    select_stmt = select_stmt.where(column.is_(None))
                else:
                    select_stmt = select_stmt.where(column == value)
        
        # Execute the query
        services = session.execute(select_stmt).fetchall()
        service_list = [row_to_dict(row) for row in services]
        
        if service_list:
            return service_list
        else:
            return None
    finally:
        session.close()


def get_service_charges(filters):
    session = SessionLocal()
    try:
        select_stmt = meteorological_services_charges.select()
        
        # Apply filters
        for key, value in filters.items():
            if value:  # Only apply filter if value is not empty
                column = getattr(meteorological_services_charges.c, key)
                if value == 'null':
                    select_stmt = select_stmt.where(column.is_(None))
                else:
                    select_stmt = select_stmt.where(column == value)
                # select_stmt = select_stmt.where(getattr(meteorological_services_charges.c, key) == value)
        
        charges = session.execute(select_stmt).fetchall()
        charge_list = [row_to_dict(row) for row in charges]
        
        if charge_list:
            return charge_list
        else:
            return None
    finally:
        session.close()

if __name__ == '__main__':
    metadata.create_all(engine)