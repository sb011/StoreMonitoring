from enum import Enum

"""
    ReportTypes Enum
    This enum is used to define the status of the report

    Attributes:
        Running (int): 1
        Completed (int): 2
"""
class ReportTypes(Enum):
    Running = 1
    Completed = 2