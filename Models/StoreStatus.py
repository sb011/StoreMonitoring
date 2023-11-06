from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""
    StoreStatus model

    This model is used to represent the store status.

    Attributes:
        id (int): The id of the store status
        store_id (int): The id of the store
        status (str): The status of the store
        timestamp_utc (DateTime): The timestamp of the store status
"""
class StoreStatus(Base):
    __tablename__ = 'store_status'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    status = Column(String)
    timestamp_utc = Column(DateTime)