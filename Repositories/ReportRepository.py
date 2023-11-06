from sqlalchemy.orm import Session
from Models.Reports import Reports
from Models.BusinessHours import BusinessHours
from Models.StoreStatus import StoreStatus
from Models.Timezones import Timezones
from Config.DBConnection import Session

"""
    This function is used to get the report by id.

    Args:
        report_id (str): The id of the report

    Returns:
        report (Reports): The report
"""
def get_report(report_id: str):
    db = Session()
    try:
        report = db.query(Reports).filter(Reports.id == report_id).first()
        return report
    finally:
        db.close()

"""
    This function is used to post the report.

    Args:
        status (str): The status of the report
"""
def update_report(report: Reports):
    db = Session()
    try:
        db.merge(report)
        db.commit()
    finally:
        db.close() 

"""
    This function is used to get the business hours.

    Returns:
        business_hours (BusinessHours): The business hours
"""
def get_business_hours():
    db = Session()
    try:
        business_hours = db.query(BusinessHours).all()
        return business_hours
    finally:
        db.close()

"""
    This function is used to get the store status.

    Args:
        start_date (DateTime): The start date
        end_date (DateTime): The end date

    Returns:
        store_status (StoreStatus): The store status
"""
def get_store_status(start_date, end_date):
    db = Session()
    try:
        store_status = db.query(StoreStatus).filter(StoreStatus.timestamp_utc >= start_date, StoreStatus.timestamp_utc < end_date).all()
        return store_status
    finally:
        db.close()

"""
    This function is used to get all the store id.

    Returns:
        store_ids (Tuple): The store ids
"""
def get_store_ids():
    db = Session()
    try:
        store_ids = db.query(StoreStatus.store_id).distinct()
        return store_ids
    finally:
        db.close()

"""
    This function is used to get the timezones.

    Returns:
        timezones (Timezones): The timezones
"""
def get_timezones():
    db = Session()
    try:
        timezones = db.query(Timezones).all()
        return timezones
    finally:
        db.close()