from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BusinessHours(Base):
    __tablename__ = 'business_hours'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    day = Column(int)
    start_time_local = Column(Time)
    end_time_local = Column(Time)