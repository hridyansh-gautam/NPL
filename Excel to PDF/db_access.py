from sqlalchemy import create_engine, Column, Integer, String, CHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Connect to database
db_name = "dcc"
user="postgres"
password="root"
host="localhost"
port="5432"
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Checksums class
class Checksums(Base):
    __tablename__ = 'checksums'
    id = Column(Integer, primary_key=True, autoincrement=True)
    checksum = Column(CHAR(64), unique=True, nullable=False)
    certificate_no = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)

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
