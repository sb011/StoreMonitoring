from sqlalchemy.orm import Session
from Models.Reports import Reports
from Models.BusinessHours import BusinessHours
from Models.StoreStatus import StoreStatus
from Models.Timezones import Timezones
from Config.DBConnection import Session

def get_report(report_id: str):
    db = Session()
    try:
        report = db.query(Reports).filter(Reports.id == report_id).first()
        return report
    finally:
        db.close()

def update_report(report: Reports):
    db = Session()
    try:
        db.merge(report)
        db.commit()
    finally:
        db.close() 

def get_business_hours():
    db = Session()
    try:
        business_hours = db.query(BusinessHours).all()
        return business_hours
    finally:
        db.close()

def get_store_status(start_date, end_date):
    db = Session()
    try:
        store_status = db.query(StoreStatus).filter(StoreStatus.timestamp_utc >= start_date, StoreStatus.timestamp_utc < end_date).all()
        return store_status
    finally:
        db.close()

def get_store_ids():
    db = Session()
    try:
        store_ids = db.query(StoreStatus.store_id).distinct()
        return store_ids
    finally:
        db.close()

def get_timezones():
    db = Session()
    try:
        timezones = db.query(Timezones).all()
        return timezones
    finally:
        db.close()