from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

url = URL.create(
    drivername="SQL Server",
    username="root",
    password="root",
    host="localhost",
    database="loopai",
    port=1433
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()