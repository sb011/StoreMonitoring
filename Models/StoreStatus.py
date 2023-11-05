from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StoreStatus(Base):
    __tablename__ = 'store_status'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    status = Column(String)
    timestamp_utc = Column(DateTime)