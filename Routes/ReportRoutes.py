from fastapi import APIRouter
from Services import ReportService

router = APIRouter()

"""
    This route is used to trigger the report
    
    Endpoint: 
        POST /trigger_report

    Returns:
        report (Reports): The report
"""
@router.post("/trigger_report")
def trigger_report():
    return ReportService.trigger_report()

"""
    This route is used to get the report by id

    Endpoint:
        GET /get_report/{report_id}

    Args:
        report_id (str): The id of the report

    Returns:
        report (Reports): The report
"""
@router.get("/get_report/{report_id}")
def get_report(report_id: str):
    return ReportService.get_report(report_id)