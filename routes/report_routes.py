from fastapi import APIRouter
from services.report_service import trigger_report, get_report

router = APIRouter()

@router.post("/trigger_report")
def trigger_report():
    return trigger_report()

@router.get("/get_report/{report_id}")
def get_report(report_id: str):
    return get_report(report_id)