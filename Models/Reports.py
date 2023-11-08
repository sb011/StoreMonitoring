from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
    Reports model

    This model is used to represent the reports.

    Attributes:
        id (int): The id of the report
        report_file (str): The name of the report file
        status (str): The status of the report
        url (str): The url of the report
"""
class Reports(Base):
    __tablename__ = 'reports'

    id = Column(String, primary_key=True, index=True)
    report_file = Column(String)
    status = Column(String)
    url = Column(String)