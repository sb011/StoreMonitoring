from pydantic import BaseModel
from typing import Dict

class Report(BaseModel):
    id: str 
    uptime_last_hour: int
    uptime_last_day: int
    uptime_last_week: int
    downtime_last_hour: int
    downtime_last_day: int
    downtime_last_week: int