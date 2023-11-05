from sqlalchemy.orm import Session
from Models.Reports import Reports
from Models.BusinessHours import BusinessHours
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