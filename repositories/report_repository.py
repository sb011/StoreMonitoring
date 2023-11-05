from fastapi import HTTPException
from sqlalchemy.orm import Session
from Models.Reports import Reports

def get_report(report_id: str):
    db = Session()
    try:
        report = db.query(Reports).filter(Reports.id == report_id).first()
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    finally:
        db.close()

    