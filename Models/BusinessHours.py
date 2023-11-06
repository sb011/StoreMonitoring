from sqlalchemy import Column, Integer, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
    BusinessHours model

    This model is used to represent the business hours of a store.

    Attributes:
        id (int): The id of the business hours
        store_id (int): The id of the store
        day_of_week (int): The day of the week
        start_time_local (Time): The start time of the business hours
        end_time_local (Time): The end time of the business hours
"""
class BusinessHours(Base):
    __tablename__ = 'business_hours'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    day_of_week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)