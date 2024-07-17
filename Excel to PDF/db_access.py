from sqlalchemy import create_engine, Column, Integer, String, CHAR, LargeBinary, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

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


# Create the table
Base.metadata.create_all(engine)

def add_checksum(data):
    # Create a new session
    Session = sessionmaker(bind=engine)
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
    Session = sessionmaker(bind=engine)
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