from sqlalchemy import Column, Integer, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BusinessHours(Base):
    __tablename__ = 'business_hours'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    day_of_week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)