import uuid
from Enums.ReportTypes import ReportTypes
from Models.Reports import Reports
from repositories import report_repository

def trigger_report():
    report = Reports()
    report.status = ReportTypes.Running
    report_id = uuid.uuid4()
    report.report_file = f"report_{report_id}.csv"

    report_repository.update_report(report)

    business_hours = report_repository.get_business_hours()

    report.status = ReportTypes.Completed
    report_repository.update_report(report)
    return {"report_id": report_id}

    

def get_report(report_id: str):
    report = report_repository.get_report(report_id)
    if report is None:
        return {"Error": "Report not found"}
    
    if report.status == "Running":
        return {"status": "Running"}
    
    return {"status": "Completed", "report": report}
    
