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

calibration_testing_table = Table(
    'calibration_testing', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('service_types', String(255)),
    Column('service_name', String(255)),
    Column('service_code', String(50), unique=True)
)

cd1_01_table = Table(
    'cd1_01', metadata,
    Column("SI_No", Integer, autoincrement=True),
    Column("Parameter", String(255)),
    Column("Item_Type_Group", String(255)),
    Column("Item_Name", String(255)),
    Column("Alias_Name", String(255)),
    Column("Range", String(255)),
    Column("No_of_Points_for_Calibration_Procedure_No", String(255)),
    Column("Limitation_Condition", String(255)),
    Column("Charges_per_Item_Rs", DECIMAL(10, 2)),
    Column("Additional_Charges_Rs", DECIMAL(10, 2)),
    Column("Description_for_Additional_Charges", Text),
    Column("Remarks_if_any", Text),
    PrimaryKeyConstraint("SI_No", "Parameter")
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
        select_stmt = calibration_testing_table.select().where(calibration_testing_table.c.id == id)
        result = session.execute(select_stmt).fetchone()
        if result:
            return dict(result)
        else:
            return None
    finally:
        session.close()