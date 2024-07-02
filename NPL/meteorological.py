from sqlalchemy import create_engine, Column, Text, String, Integer, MetaData, Table, DECIMAL, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict

db_name = "npl"
user = "postgres"
password = "clearpointdivine"
host = "localhost"
port = "5432"
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

meteorological_classification = Table(
    'meteorological_classification', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('service_types', String(255)),
    Column('service_name', String(255)),
    Column('service_code', String(50), unique=True)
)

def add_new_service(data: dict):
    session = SessionLocal()
    try:
        insert_stmt = cd1_01_table.insert().values(**data)
        session.execute(insert_stmt)
        session.commit()
        return 'Service successfully added'
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_service(id: int):
    session = SessionLocal()
    try:
        select_stmt = meteorological_classification.select().where(meteorological_classification.c.id == id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()