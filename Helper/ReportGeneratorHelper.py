import os
import pytz
import concurrent.futures
import pandas as pd
from datetime import datetime, timedelta
from Enums.ReportTypes import ReportTypes
from Repositories import ReportRepository
from Models.Reports import Reports
from Helper.CloudinaryHelper import upload_file

"""
    This function generates the report and uploads it to cloudinary

    Args:
        report (Reports): The report object
    
    Returns:
        url (str): The url of the uploaded file
"""
def generate_report(report: Reports):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    # get all the data from the database
    business_hours = ReportRepository.get_business_hours()
    store_status = ReportRepository.get_store_status(start_date, end_date)
    timezones = ReportRepository.get_timezones()

    # make list of store unique ids
    store_ids = list(set([x.store_id for x in business_hours]))
    # store_ids = [2567728765809290933]

    # calculate the uptime and downtime
    results = []
    # Using ThreadPoolExecutor to parallelize the for loop
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Define a lambda function to pass arguments to calculate_uptime_downtime in parallel
        calculate_partial = lambda store_id: calculate_uptime_downtime(store_id, business_hours, store_status, timezones)
        # Use executor.map() to apply the lambda function to store_ids in parallel
        results = list(executor.map(calculate_partial, store_ids))

    # save the results to a csv file and store it in csv folder
    df = pd.DataFrame(results)
    df.to_csv(report.report_file, index=False)
    
    # upload the file to cloudinary
    url = upload_file(report.report_file)
    
    # remove the file from the csv folder
    os.remove(report.report_file)

    report.url = url
    report.status = ReportTypes.Completed.value
    ReportRepository.update_report(report)


"""
    This function calculates the uptime and downtime for a store

    Args:
        store_id (str): The id of the store
        business_hours (list): The list of business hours
        store_status (list): The list of store status
        timezones (list): The list of timezones
        
    Returns:
        dict: The dictionary containing the uptime and downtime    
"""
def calculate_uptime_downtime(store_id: str, business_hours: list, store_status: list, timezones: list): 
    # get the business hours, store status and timezone for the store   
    store_business_hours = [x for x in business_hours if x.store_id == store_id]
    store_business_status = [x for x in store_status if x.store_id == store_id]

    # get the timezone for the store
    timezone_str = "America/Chicago"
    timezone_entry = next((x for x in timezones if x.store_id == store_id), None)
    if timezone_entry:
        timezone_str = timezone_entry.timezone_str

    # Using ThreadPoolExecutor to run the functions in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the functions to the executor with necessary parameters
        downtime_future = executor.submit(calculate_downtime, store_business_hours, store_business_status, timezone_str)
        uptime_future = executor.submit(calculate_uptime, store_business_hours, timezone_str)

        # Wait for all futures to complete and get the results
        downtime_last_hour, downtime_last_day, downtime_last_week = downtime_future.result()
        uptime_last_hour, uptime_last_day, uptime_last_week = uptime_future.result()
    
    # subtract the downtime from uptime
    if uptime_last_hour != 0:
        uptime_last_hour -= downtime_last_hour
    if uptime_last_day != 0:
        uptime_last_day -= downtime_last_day
    if uptime_last_week != 0:
        uptime_last_week -= downtime_last_week

    return {   
        "store_id": store_id,
        "downtime_last_hour (in minutes)": downtime_last_hour,
        "downtime_last_day (in hours)": downtime_last_day,
        "downtime_last_week (in hours)": downtime_last_week,
        "uptime_last_hour (in minutes)": uptime_last_hour,
        "uptime_last_day (in hours)": uptime_last_day,
        "uptime_last_week (in hours)": uptime_last_week
    }

"""
    This function calculates the downtime for the last hour

    Args:
        store_business_hours (list): The list of business hours
        store_business_status (list): The list of store status
        timezone (str): The timezone of the store

    Returns:
        int: The downtime in minutes
"""
def get_last_hour_downtime(store_business_status: list, timezone: str):
    current_time_local = datetime.now(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)
    last_hour_local = current_time_local - timedelta(hours=1)

    downtime_minutes = 0
    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_local = status_entry.timestamp_utc.astimezone(pytz.timezone(timezone))
            if last_hour_local <= status_timestamp_local <= current_time_local:
                next_active_status = next((s.timestamp_utc.astimezone(pytz.timezone(timezone)) for s in store_business_status
                                           if s.status == 'active' and last_hour_local <= s.timestamp_utc.astimezone(pytz.timezone(timezone)) <= current_time_local), None)
                if next_active_status:
                    downtime_minutes += (next_active_status.replace(tzinfo=pytz.UTC) - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
                else:
                    downtime_minutes += (current_time_local.replace(tzinfo=pytz.UTC) - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
    return max(downtime_minutes, 0)

"""
    This function calculates the downtime for the last day

    Args:
        store_business_hours (list): The list of business hours
        store_business_status (list): The list of store status
        timezone (str): The timezone of the store

    Returns:
        int: The downtime in minutes
"""
def get_last_day_downtime(store_business_status: list, timezone: str):
    current_time_local = datetime.now(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_day_local = current_time_local - timedelta(days=1)

    downtime_minutes = 0
    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_local = status_entry.timestamp_utc.astimezone(pytz.timezone(timezone))
            if last_day_local <= status_timestamp_local <= current_time_local:
                next_active_status = next((s.timestamp_utc.astimezone(pytz.timezone(timezone)) for s in store_business_status
                                           if s.status == 'active' and last_day_local <= s.timestamp_utc.astimezone(pytz.timezone(timezone)) <= current_time_local), None)
                if next_active_status:
                    downtime_minutes += (next_active_status.replace(tzinfo=pytz.UTC) - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
                else:
                    downtime_minutes += (current_time_local.replace(tzinfo=pytz.UTC) - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
    return max(downtime_minutes, 0)

"""
    This function calculates the downtime for the last week

    Args:
        store_business_hours (list): The list of business hours
        store_business_status (list): The list of store status
        timezone (str): The timezone of the store
    
    Returns:
        int: The downtime in minutes
"""
def get_last_week_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    downtime_minutes = 0
    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_local = status_entry.timestamp_utc.astimezone(pytz.timezone(timezone))
            for business_hours_entry in store_business_hours:
                if business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    start_time_local = datetime.combine(status_timestamp_local.date(), business_hours_entry.start_time_local).replace(tzinfo=pytz.UTC)
                    end_time_local = datetime.combine(status_timestamp_local.date(), business_hours_entry.end_time_local).replace(tzinfo=pytz.UTC)
                    if start_time_local.time() <= status_timestamp_local.time() <= end_time_local.time():
                        next_active_status = next((s.timestamp_utc.astimezone(pytz.timezone(timezone)) for s in store_business_status
                                                   if s.status == 'active' and start_time_local <= s.timestamp_utc.astimezone(pytz.timezone(timezone)) <= end_time_local), None)
                        if next_active_status:
                            downtime_minutes += (next_active_status.replace(tzinfo=pytz.UTC) - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
                        else:
                            downtime_minutes += (end_time_local - status_timestamp_local.replace(tzinfo=pytz.UTC)).total_seconds() / 60
    
    return max(downtime_minutes, 0)

"""
    This function calculates the uptime for the last hour

    Args:
        store_business_hours (list): The list of business hours
        timezone (str): The timezone of the store

    Returns:
        int: The uptime in minutes
"""
def get_last_hour_uptime(store_business_hours: list, timezone: str):
    current_time_local = datetime.now(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)
    one_hour_ago_local = current_time_local - timedelta(hours=1)

    uptime_minutes = 0
    for business_hours_entry in store_business_hours:
        if business_hours_entry.day_of_week == one_hour_ago_local.weekday():
            start_time_local = datetime.combine(one_hour_ago_local.date(), business_hours_entry.start_time_local).astimezone(pytz.timezone(timezone))
            end_time_local = datetime.combine(one_hour_ago_local.date(), business_hours_entry.end_time_local).astimezone(pytz.timezone(timezone))
            if start_time_local <= one_hour_ago_local <= end_time_local and start_time_local <= current_time_local <= end_time_local:
                uptime_minutes += 60
            elif start_time_local <= one_hour_ago_local <= end_time_local and current_time_local > end_time_local:
                uptime_minutes += (end_time_local - one_hour_ago_local).total_seconds() / 60
            elif start_time_local <= current_time_local <= end_time_local and one_hour_ago_local < start_time_local:
                uptime_minutes += (current_time_local - start_time_local).total_seconds() / 60
            
    return uptime_minutes

"""
    This function calculates the uptime for the last day

    Args:
        store_business_hours (list): The list of business hours
        timezone (str): The timezone of the store

    Returns:
        int: The uptime in minutes
"""
def get_last_day_uptime(store_business_hours: list, timezone: str):
    current_time_local = datetime.now(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
    one_day_ago_local = current_time_local - timedelta(days=1)

    uptime_minutes = 0
    for business_hours_entry in store_business_hours:
        if business_hours_entry.day_of_week == one_day_ago_local.weekday():
            start_time_local = datetime.combine(one_day_ago_local.date(), business_hours_entry.start_time_local).astimezone(pytz.timezone(timezone))
            end_time_local = datetime.combine(one_day_ago_local.date(), business_hours_entry.end_time_local).astimezone(pytz.timezone(timezone))
            
            uptime_minutes += ((end_time_local - start_time_local).total_seconds() / 60)
    return uptime_minutes

"""
    This function calculates the uptime for the last week

    Args:
        store_business_hours (list): The list of business hours

    Returns:
        int: The uptime in minutes
"""
def get_last_week_uptime(store_business_hours: list):
    uptime_minutes = 0
    for business_hours_entry in store_business_hours:
        uptime_minutes += (business_hours_entry.end_time_local.hour - business_hours_entry.start_time_local.hour) * 60
    return uptime_minutes

"""
    This function calculates the downtime for the last hour

    Args:
        store_business_hours (list): The list of business hours
        store_business_status (list): The list of store status
        timezone_str (str): The timezone of the store

    Returns:
        downtime_last_hour (int): The downtime in minutes
        downtime_last_day (int): The downtime in minutes
        downtime_last_week (int): The downtime in minutes
"""
def calculate_downtime(store_business_hours, store_business_status, timezone_str):
    # calculate the downtime
    downtime_last_hour = int(get_last_hour_downtime(store_business_status, timezone_str))
    downtime_last_day = int(get_last_day_downtime(store_business_status, timezone_str) / 60)
    downtime_last_week = int(get_last_week_downtime(store_business_hours, store_business_status, timezone_str) / 60)
    return downtime_last_hour, downtime_last_day, downtime_last_week

"""
    This function calculates the uptime for the last hour

    Args:
        store_business_hours (list): The list of business hours
        store_business_status (list): The list of store status
        timezone_str (str): The timezone of the store

    Returns:
        uptime_last_hour (int): The uptime in minutes
        uptime_last_day (int): The uptime in minutes
        uptime_last_week (int): The uptime in minutes
"""
def calculate_uptime(store_business_hours, timezone_str):
    # calculate the uptime and subtract the downtime
    uptime_last_hour = int(get_last_hour_uptime(store_business_hours, timezone_str))
    uptime_last_day =int(get_last_day_uptime(store_business_hours, timezone_str) / 60)
    uptime_last_week = int(get_last_week_uptime(store_business_hours) / 60)
    return uptime_last_hour, uptime_last_day, uptime_last_week