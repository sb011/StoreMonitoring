from fastapi import APIRouter
from services import report_service

router = APIRouter()

@router.post("/trigger_report")
def trigger_report():
    return report_service.trigger_report()

@router.get("/get_report/{report_id}")
def get_report(report_id: str):
    return report_service.get_report(report_id)