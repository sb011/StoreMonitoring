from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Reports(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    report_file = Column(String)
    status = Column(String)