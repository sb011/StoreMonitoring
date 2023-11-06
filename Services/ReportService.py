import threading
import uuid
from Enums.ReportTypes import ReportTypes
from Models.Reports import Reports
from Repositories import ReportRepository
from Helper.ReportGeneratorHelper import generate_report

def trigger_report():
    report = Reports()
    report_id = uuid.uuid4()
    report.status = ReportTypes.Running.value
    report.report_file = f"report_{report_id}.csv"
    ReportRepository.update_report(report)

    url = generate_report(report)
    report.url = url
    report.status = ReportTypes.Completed.value
    ReportRepository.update_report(report)
    return {"report_id": report_id}

def get_report(report_id: str):
    report = ReportRepository.get_report(report_id)
    if report is None:
        return {"Error": "Report not found"}
    
    if report.status == "Running":
        return {"status": "Running"}
    
    return {"status": "Completed", "report": report}