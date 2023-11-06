from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
    Timezones model

    This model is used to represent the timezones.

    Attributes:
        id (int): The id of the timezone
        store_id (int): The id of the store
        timezone_str (DateTime): The timezone of the store
"""
class Timezones(Base):
    __tablename__ = 'timezones'

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    timezone_str = Column(DateTime)