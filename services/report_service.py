import uuid
from models.report import Report
from repositories.report_repository import get_report

def trigger_report():
    report = Report()
    report.status = "Running"
    report_id = uuid.uuid4()
    report.report_file = f"report_{report_id}.csv"
    

def get_report(report_id: str):
    report = get_report(report_id)
    if report is None:
        return {"status": "Report not found"}
    
    if report.status == "Running":
        return {"status": "Report generation in progress"}
    
    return {"status": "Report generated successfully", report: report}
    
