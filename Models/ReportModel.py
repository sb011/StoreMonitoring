"""
    ReportModel

    This class is used to store the data of the report

    Attributes:
        store_id (str): The id of the store
        uptime_last_hour (str): The uptime of the store in the last hour
        uptime_last_day (str): The uptime of the store in the last day
        update_last_week (str): The uptime of the store in the last week
        downtime_last_hour (str): The downtime of the store in the last hour
        downtime_last_day (str): The downtime of the store in the last day
        downtime_last_week (str): The downtime of the store in the last week
"""
class ReportModel:
    def __init__(self):
        self.store_id = ""
        self.uptime_last_hour = ""
        self.uptime_last_day = ""
        self.update_last_week = ""
        self.downtime_last_hour = ""
        self.downtime_last_day = ""
        self.downtime_last_week = ""