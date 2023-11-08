import os
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
    # Create a report
    report = Reports()

    # Set the report status to running
    report.id = uuid.uuid4()
    report.status = ReportTypes.Running.value
    report.report_file = f"report_{report.id}.csv"
    ReportRepository.update_report(report)

    # Generate the report
    url = generate_report(report)

    # Update the report to completed
    report.url = url
    report.status = ReportTypes.Completed.value
    ReportRepository.update_report(report)
    return {"report_id": report.id}

"""
    This function is used to get the report by id.

    Args:
        report_id (str): The id of the report
    
    Returns:
        report (Reports): The report
"""
def get_report(report_id: str):
    report = ReportRepository.get_report(report_id)

    # Check if the report exists
    if report is None:
        return {"Error": "Report not found"}
    
    # Check if the report is running
    if report.status == "Running":
        return {"status": "Running"}
    
    return {"status": "completed", "report": report.url}