import threading
import uuid

from fastapi.responses import FileResponse
from Enums.ReportTypes import ReportTypes
from Models.Reports import Reports
from Repositories import ReportRepository
from Helper.ReportGeneratorHelper import generate_report

"""
    This function is used to trigger the report.

    Returns:
        report_id (str): The id of the report
"""
def trigger_report():
    try:
        # Create a report
        report = Reports()

        # Set the report status to running
        report.id = uuid.uuid4()
        report.status = ReportTypes.Running.value
        report.report_file = f"report_{report.id}.csv"
        ReportRepository.update_report(report)

        # Generate the report
        task = threading.Thread(target = generate_report, args = (report,))
        task.start()

        return {"report_id": report.id}
    except:
        return {"Error": "Report generation failed"}

"""
    This function is used to get the report by id.

    Args:
        report_id (str): The id of the report
    
    Returns:
        report (Reports): The report
"""
def get_report(report_id: str):
    try:
        report = ReportRepository.get_report(report_id)

        # Check if the report exists
        if report is None:
            return {"Error": "Report not found"}
        
        # Check if the report is running
        if report.status == ReportTypes.Running.value:
            return {"status": "Running"}
        
        return {"status": "completed", "report": report.url}
    except:
        return {"Error": "Get report failed"}