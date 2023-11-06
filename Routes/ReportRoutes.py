from fastapi import APIRouter
from Services import ReportService

router = APIRouter()

@router.post("/trigger_report")
def trigger_report():
    return ReportService.trigger_report()

@router.get("/get_report/{report_id}")
def get_report(report_id: str):
    return ReportService.get_report(report_id)