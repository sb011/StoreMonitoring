import os
import pytz
import pandas as pd
from datetime import datetime, timedelta
from Repositories import ReportRepository
from Models.Reports import Reports
from CloudinaryHelper import upload_file

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
    store_ids = ReportRepository.get_store_ids()
    business_hours = ReportRepository.get_business_hours()
    store_status = ReportRepository.get_store_status(start_date, end_date)
    timezones = ReportRepository.get_timezones()
    
    # calculate the uptime and downtime
    results = []
    for store_id in store_ids:
        results.append(calculate_uptime_downtime(store_id, business_hours, store_status, timezones, start_date, end_date))

    # save the results to a csv file
    df = pd.DataFrame(results)
    df.to_csv(report.report_file, index=False)

    # upload the file to cloudinary
    url = upload_file(report.report_file).url

    # remove the file from the server
    os.remove(report.report_file)

    return url

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
    timezone = [x for x in timezones if x.store_id == store_id]
    timezone_str = "America/Chicago"
    if len(timezone) > 0:    
        timezone_str = timezone[0].timezone_str
    
    # calculate the downtime
    downtime_last_hour = get_last_hour_downtime(store_business_hours, store_business_status, timezone_str)
    downtime_last_day = get_last_day_downtime(store_business_hours, store_business_status, timezone_str) / 60
    downtime_last_week = get_last_week_downtime(store_business_hours, store_business_status, timezone_str) / 60

    # calculate the uptime and subtract the downtime
    uptime_last_hour = get_last_hour_uptime(store_business_hours, timezone_str)
    if uptime_last_hour != 0:
        uptime_last_hour -= downtime_last_hour
    uptime_last_day = get_last_day_uptime(store_business_hours, timezone_str) / 60
    if uptime_last_day != 0:
        uptime_last_day -= downtime_last_day
    uptime_last_week = get_last_week_uptime(store_business_hours) / 60
    if uptime_last_week != 0:
        uptime_last_week -= downtime_last_week

    return {   
        "store_id": store_id,
        "downtime_last_hour": int(downtime_last_hour),
        "downtime_last_day": int(downtime_last_day),
        "downtime_last_week": int(downtime_last_week),
        "uptime_last_hour": int(uptime_last_hour),
        "uptime_last_day": int(uptime_last_day),
        "uptime_last_week": int(uptime_last_week)
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
def get_last_hour_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    # get the current time in utc and convert it to local time
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)

    # get the last hour in local time
    last_hour_local = current_time_local - timedelta(hours=1)

    downtime_minutes = 0
    # iterate through the store status
    for status_entry in store_business_status:
        # check if the status is inactive
        if status_entry.status == 'inactive':
            # get the timestamp of the status and convert it to local time
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))
            
            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                # check if the day of week is the same for the status and business hours
                if business_hours_entry.day_of_week == current_time_local.weekday() and business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    # get the start and end time of the business hours and convert it to local time
                    start_time_local = business_hours_entry.start_time_local
                    end_time_local = business_hours_entry.end_time_local
                    start_datetime_local = datetime.combine(current_time_local.date(), start_time_local).astimezone(pytz.timezone(timezone))
                    end_datetime_local = datetime.combine(current_time_local.date(), end_time_local).astimezone(pytz.timezone(timezone))
                    
                    # case 1: last_hour_local is in working hours and current_time_local is in working hours
                    if start_datetime_local <= last_hour_local <= end_datetime_local and start_datetime_local <= current_time_local <= end_datetime_local:
                        # the timestamp should be between the last hour and the current time
                        if last_hour_local <= status_timestamp_local <= current_time_local:
                            # count the minutes from the timestamp to next active status 
                            # which should be less than current_time_local and greater than last_hour_local
                            for status_entry in store_business_status:
                                if status_entry.status == 'active':
                                    next_status_timestamp_utc = status_entry.timestamp_utc
                                    next_status_timestamp_local = next_status_timestamp_utc.astimezone(pytz.timezone(timezone))
                                    if last_hour_local <= next_status_timestamp_local <= current_time_local:
                                        downtime_minutes += (next_status_timestamp_local - status_timestamp_local).total_seconds() / 60
                                    break
                            else:
                                downtime_minutes += (current_time_local - status_timestamp_local).total_seconds() / 60
                    # case 2: last_hour_local is in working hours and current_time_local is not in working hours
                    elif start_datetime_local <= last_hour_local <= end_datetime_local and not (start_datetime_local <= current_time_local <= end_datetime_local):
                        # the timestamp should be between the last hour and end of working hours
                        if last_hour_local <= status_timestamp_local <= end_datetime_local:
                            # count the minutes from the timestamp to next active status 
                            # which should be less than end_datetime_local and greater than last_hour_local
                            for status_entry in store_business_status:
                                if status_entry.status == 'active':
                                    next_status_timestamp_utc = status_entry.timestamp_utc
                                    next_status_timestamp_local = next_status_timestamp_utc.astimezone(pytz.timezone(timezone))
                                    if last_hour_local <= next_status_timestamp_local <= end_datetime_local:
                                        downtime_minutes += (next_status_timestamp_local - status_timestamp_local).total_seconds() / 60
                                    break
                            else:
                                downtime_minutes += (end_datetime_local - status_timestamp_local).total_seconds() / 60
                    # case 3: last_hour_local is not in working hours and current_time_local is in working hours
                    elif not (start_datetime_local <= last_hour_local <= end_datetime_local) and start_datetime_local <= current_time_local <= end_datetime_local:
                        # the timestamp should be between start of working hours and current_time_local
                        if start_datetime_local <= status_timestamp_local <= current_time_local:
                            # count the minutes from the timestamp to next active status 
                            # which should be less than current_time_local and greater than start_datetime_local
                            for status_entry in store_business_status:
                                if status_entry.status == 'active':
                                    next_status_timestamp_utc = status_entry.timestamp_utc
                                    next_status_timestamp_local = next_status_timestamp_utc.astimezone(pytz.timezone(timezone))
                                    if start_datetime_local <= next_status_timestamp_local <= current_time_local:
                                        downtime_minutes += (next_status_timestamp_local - status_timestamp_local).total_seconds() / 60
                                    break
                            else:
                                downtime_minutes += (current_time_local - status_timestamp_local).total_seconds() / 60
                    # case 4: last_hour_local is not in working hours and current_time_local is not in working hours
                    elif not (start_datetime_local <= last_hour_local <= end_datetime_local) and not (start_datetime_local <= current_time_local <= end_datetime_local):
                        return 0


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
def get_last_day_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    # get the current time in utc and convert it to local time
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)

    # get the last day in local time
    last_day_local = current_time_local - timedelta(days=1)
    downtime_minutes = 0

    # iterate through the store status
    for status_entry in store_business_status:
        # check if the status is inactive
        if status_entry.status == 'inactive':
            # get the timestamp of the status and convert it to local time
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))
            
            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                # check if the day of week is the same for the status and business hours
                if business_hours_entry.day_of_week == last_day_local.weekday() and business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    # get the start and end time of the business hours and convert it to local time
                    start_time_local = business_hours_entry.start_time_local
                    end_time_local = business_hours_entry.end_time_local
                    start_datetime_local = datetime.combine(status_timestamp_local.date(), start_time_local).astimezone(pytz.timezone(timezone))
                    end_datetime_local = datetime.combine(status_timestamp_local.date(), end_time_local).astimezone(pytz.timezone(timezone))

                    # case 1: status_timestamp_local is in working hours 
                    # count the minutes from the timestamp to next active status which should be less than end_local and greater than start_local
                    if start_datetime_local <= status_timestamp_local <= end_datetime_local:
                        for status_entry in store_business_status:
                            if status_entry.status == 'active':
                                next_status_timestamp_utc = status_entry.timestamp_utc
                                next_status_timestamp_local = next_status_timestamp_utc.astimezone(pytz.timezone(timezone))
                                if start_datetime_local <= next_status_timestamp_local <= end_datetime_local:
                                    downtime_minutes += (next_status_timestamp_local - status_timestamp_local).total_seconds() / 60
                                break
                        else:
                            downtime_minutes += (end_datetime_local - status_timestamp_local).total_seconds() / 60
    
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

    # iterate through the store status
    for status_entry in store_business_status:
        # check if the status is inactive
        if status_entry.status == 'inactive':
            # get the timestamp of the status and convert it to local time
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))

            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                # check if the day of week is the same for the status and business hours
                if business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    # get the start and end time of the business hours and convert it to local time
                    start_time_local = business_hours_entry.start_time_local
                    end_time_local = business_hours_entry.end_time_local
                    start_datetime_local = datetime.combine(status_timestamp_local.date(), start_time_local).astimezone(pytz.timezone(timezone))
                    end_datetime_local = datetime.combine(status_timestamp_local.date(), end_time_local).astimezone(pytz.timezone(timezone))
            
                    # case 1: status_timestamp_local is in working hours and count the minutes from the timestamp to next active status which should be less than end_local and greater than start_local
                    if start_datetime_local <= status_timestamp_local <= end_datetime_local:
                        for status_entry in store_business_status:
                            if status_entry.status == 'active':
                                next_status_timestamp_utc = status_entry.timestamp_utc
                                next_status_timestamp_local = next_status_timestamp_utc.astimezone(pytz.timezone(timezone))
                                if start_datetime_local <= next_status_timestamp_local <= end_datetime_local:
                                    downtime_minutes += (next_status_timestamp_local - status_timestamp_local).total_seconds() / 60
                                break
                        else:
                            downtime_minutes += (end_datetime_local - status_timestamp_local).total_seconds() / 60

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
    # get the current time in utc and convert it to local time
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)

    # get the last hour in local time
    one_hour_ago_local = current_time_local - timedelta(hours=1)
    one_hour_ago_local_time = one_hour_ago_local.time()

    # iterate through the business hours
    for business_hours_entry in store_business_hours:
        # check if the day of week is the same for the business hours and last hour
        if business_hours_entry.day_of_week == one_hour_ago_local.weekday():
            start_time_local = business_hours_entry.start_time_local
            end_time_local = business_hours_entry.end_time_local
            
            # case1: one_hour_ago_local is in working hours and current_time_local is in working hours
            if start_time_local <= one_hour_ago_local_time <= end_time_local and start_time_local <= current_time_local.time() <= end_time_local:
                return 60
            # case2: one_hour_ago_local is in working hours and current_time_local is not in working hours
            elif start_time_local <= one_hour_ago_local_time <= end_time_local and not (start_time_local <= current_time_local.time() <= end_time_local):
                return (end_time_local.hour - one_hour_ago_local_time.hour) * 60
            # case3: one_hour_ago_local is not in working hours and current_time_local is in working hours
            elif not (start_time_local <= one_hour_ago_local_time <= end_time_local) and start_time_local <= current_time_local.time() <= end_time_local:
                return (current_time_local.time().hour - start_time_local.hour) * 60
            # case4: one_hour_ago_local is not in working hours and current_time_local is not in working hours
            elif not (start_time_local <= one_hour_ago_local_time <= end_time_local) and not (start_time_local <= current_time_local.time() <= end_time_local):
                return 0

    return 0

"""
    This function calculates the uptime for the last day

    Args:
        store_business_hours (list): The list of business hours
        timezone (str): The timezone of the store

    Returns:
        int: The uptime in minutes
"""
def get_last_day_uptime(store_business_hours: list, timezone: str):
    # get the current time in utc and convert it to local time
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)

    # get the last day in local time
    one_day_ago_local = current_time_local - timedelta(days=1)
    uptime_minutes = 0

    # iterate through the business hours
    for business_hours_entry in store_business_hours:
        # check if the day of week is the same for the business hours and last day
         if business_hours_entry.day_of_week == one_day_ago_local.weekday():
            start_time_local = business_hours_entry.start_time_local
            end_time_local = business_hours_entry.end_time_local
            # case1: calculate the uptime for the last day
            uptime_minutes += (end_time_local.hour - start_time_local.hour) * 60

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

    # iterate through the business hours
    for business_hours_entry in store_business_hours:
        # calculate the uptime for the last week
        start_time_local = business_hours_entry.start_time_local
        end_time_local = business_hours_entry.end_time_local
        # case1: sum all the working hours
        uptime_minutes += (end_time_local.hour - start_time_local.hour) * 60

    return uptime_minutes