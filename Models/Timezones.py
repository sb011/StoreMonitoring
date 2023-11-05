from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Timezones(Base):
    __tablename__ = 'timezones'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    timezone_str = Column(DateTime)