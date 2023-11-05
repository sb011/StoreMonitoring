from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

url = "mssql+pyodbc://root:root@localhost/loopai?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(url, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()