from sqlalchemy import create_engine, Column, Integer, String, CHAR, LargeBinary, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import hashlib

# Connect to database
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Checksums class
class Checksums(Base):
    __tablename__ = 'checksums'
    id = Column(Integer, primary_key=True, autoincrement=True)
    checksum = Column(CHAR(64), unique=True, nullable=False)
    certificate_no = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)

class Emp_reg(Base):
    __tablename__ = 'emp_reg'
    emp_reg_id = Column(Integer, primary_key=True)
    f_name = Column(String(100))
    l_name = Column(String(100))
    emp_id = Column(String(255))
    email = Column(String(255), unique=True)
    mobile_no = Column(String(20))
    designation = Column(String(50))
    addr_1 = Column(Text)
    password = Column(String(255))
    signature = Column(LargeBinary)

class DccPdf(Base):
    __tablename__ = 'dcc_pdf'
    pdf_serial_id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_directory = Column(String(255))
    current_stage = Column(Integer)
    calibrated_by = Column(String(255))
    checked_by = Column(String(255))
    scientist_in_charge = Column(String(255))
    issued_by = Column(String(255))
    version = Column(Integer)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_checksum(data):
    # Create a new session
    session = Session()

    existing_row = session.query(Checksums).filter_by(certificate_no=data['certificate_no']).first()

    curr_status = data['status']
    # If such a row exists, delete it
    if existing_row:
        session.delete(existing_row)
        session.commit()
        curr_status = existing_row.status

    # Insert a new row
    new_checksum = Checksums(
        checksum=data['checksum'],
        certificate_no=data['certificate_no'],
        status=curr_status
    )
    
    # Add the new row to the session and commit
    session.add(new_checksum)
    session.commit()
    # Close the session
    session.close()
    
    return "New checksum added to the checksums table."

def get_signature(name=None, emp_id=None):
    session = Session()
    query = session.query(Emp_reg)
    
    # Add filters based on parameters
    if name:
        combined_name = Emp_reg.f_name + ' ' + Emp_reg.l_name
        query = query.filter(combined_name.ilike(f'%{name}%'))
    
    if emp_id:
        query = query.filter(Emp_reg.emp_id == emp_id)
    
    employee = query.first()  # Retrieve the first matching employee
    
    if employee:
        return employee.signature
    else:
        return None

def generate_checksum(file_path, algorithm='sha256'):
    """
    Generate a checksum for a given file using the specified algorithm.

    :param file_path: Path to the file.
    :param algorithm: Hashing algorithm to use (default: 'sha256').
    :return: Checksum of the file.
    """
    hash_function = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read():
            hash_function.update(chunk)
    return hash_function.hexdigest()

def insert_pdf_record(pdf_directory, current_stage=None,  calibrated_by=None, checked_by=None, scientist_in_charge=None, issued_by=None, version=1):
    session = Session()
    pdf_record = DccPdf(pdf_directory=pdf_directory,
                        current_stage=current_stage,
                        calibrated_by=calibrated_by,
                        checked_by=checked_by,
                        scientist_in_charge=scientist_in_charge,
                        issued_by=issued_by,
                        version=version)
    session.add(pdf_record)
    session.commit()
    session.close()

def update_pdf_stage(pdf_serial_id, new_stage):
    session = Session()
    stmt = update(DccPdf).where(DccPdf.pdf_serial_id == pdf_serial_id).values(
        current_stage=new_stage,
        version=DccPdf.version + 1
    )
    session.execute(stmt)
    session.commit()
    session.close()

def get_current_stage(pdf_serial_id):
    session = Session()
    current_stage = session.query(DccPdf.current_stage).filter_by(pdf_serial_id=pdf_serial_id).scalar()
    session.close()
    return current_stage

def get_version(pdf_serial_id):
    session = Session()
    version = session.query(DccPdf.version).filter_by(pdf_serial_id=pdf_serial_id).scalar()
    session.close()
    return version

def pdf_exists(pdf_directory):
    session = Session()
    exists = session.query(DccPdf).filter_by(pdf_directory=pdf_directory).first() is not None
    session.close()
    return exists
