import os
import pytz
import pandas as pd
from datetime import datetime, timedelta
from Repositories import ReportRepository
from Models.Reports import Reports
from CloudinaryHelper import upload_file

def generate_report(report: Reports):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    store_ids = ReportRepository.get_store_ids()
    business_hours = ReportRepository.get_business_hours()
    store_status = ReportRepository.get_store_status(start_date, end_date)
    timezones = ReportRepository.get_timezones()
    
    results = []
    for store_id in store_ids:
        results.append(calculate_uptime_downtime(store_id, business_hours, store_status, timezones, start_date, end_date))

    df = pd.DataFrame(results)
    df.to_csv(report.report_file, index=False)

    url = upload_file(report.report_file).url
    os.remove(report.report_file)

    return url


def calculate_uptime_downtime(store_id: str, business_hours: list, store_status: list, timezones: list, start_date: datetime, end_date: datetime):    
    store_business_hours = [x for x in business_hours if x.store_id == store_id]
    store_business_status = [x for x in store_status if x.store_id == store_id]
    
    timezone = [x for x in timezones if x.store_id == store_id]
    timezone_str = "America/Chicago"
    if len(timezone) > 0:    
        timezone_str = timezone[0].timezone_str
    
    downtime_last_hour = get_last_hour_downtime(store_business_hours, store_business_status, timezone_str)
    downtime_last_day = get_last_day_downtime(store_business_hours, store_business_status, timezone_str) / 60
    downtime_last_week = get_last_week_downtime(store_business_hours, store_business_status, timezone_str) / 60

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

def get_last_hour_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)
    last_hour_local = current_time_local - timedelta(hours=1)

    downtime_minutes = 0

    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))
            
            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                if business_hours_entry.day_of_week == current_time_local.weekday() and business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    start_time_local = business_hours_entry.start_time_local
                    end_time_local = business_hours_entry.end_time_local
                    start_datetime_local = datetime.combine(current_time_local.date(), start_time_local).astimezone(pytz.timezone(timezone))
                    end_datetime_local = datetime.combine(current_time_local.date(), end_time_local).astimezone(pytz.timezone(timezone))
                    
                    # case 1: last_hour_local is in working hours and current_time_local is in working hours
                    if start_datetime_local <= last_hour_local <= end_datetime_local and start_datetime_local <= current_time_local <= end_datetime_local:
                        # the timestamp should be between the last hour and the current time
                        if last_hour_local <= status_timestamp_local <= current_time_local:
                            # count the minutes from the timestamp to next active status which should be less than current_time_local and greater than last_hour_local
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
                            # count the minutes from the timestamp to next active status which should be less than end_datetime_local and greater than last_hour_local
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
                            # count the minutes from the timestamp to next active status which should be less than current_time_local and greater than start_datetime_local
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

def get_last_day_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_day_local = current_time_local - timedelta(days=1)
    downtime_minutes = 0

    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))
            
            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                if business_hours_entry.day_of_week == last_day_local.weekday() and business_hours_entry.day_of_week == status_timestamp_local.weekday():
                    start_time_local = business_hours_entry.start_time_local
                    end_time_local = business_hours_entry.end_time_local
                    start_datetime_local = datetime.combine(status_timestamp_local.date(), start_time_local).astimezone(pytz.timezone(timezone))
                    end_datetime_local = datetime.combine(status_timestamp_local.date(), end_time_local).astimezone(pytz.timezone(timezone))
                    print(start_datetime_local, end_datetime_local, status_timestamp_local)
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


def get_last_week_downtime(store_business_hours: list, store_business_status: list, timezone: str):
    downtime_minutes = 0

    for status_entry in store_business_status:
        if status_entry.status == 'inactive':
            status_timestamp_utc = status_entry.timestamp_utc
            status_timestamp_local = status_timestamp_utc.astimezone(pytz.timezone(timezone))

            # check if timestamp is in working hours
            for business_hours_entry in store_business_hours:
                if business_hours_entry.day_of_week == status_timestamp_local.weekday():
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

def get_last_hour_uptime(store_business_hours: list, timezone: str):
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)

    one_hour_ago_local = current_time_local - timedelta(hours=1)
    one_hour_ago_local_time = one_hour_ago_local.time()

    for business_hours_entry in store_business_hours:
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

def get_last_day_uptime(store_business_hours: list, timezone: str):
    current_time_utc = datetime.now(pytz.utc)
    current_time_local = current_time_utc.astimezone(pytz.timezone(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)

    one_day_ago_local = current_time_local - timedelta(days=1)
    uptime_minutes = 0
    for business_hours_entry in store_business_hours:
         if business_hours_entry.day_of_week == one_day_ago_local.weekday():
            start_time_local = business_hours_entry.start_time_local
            end_time_local = business_hours_entry.end_time_local
            uptime_minutes += (end_time_local.hour - start_time_local.hour) * 60

    return uptime_minutes

def get_last_week_uptime(store_business_hours: list):
    uptime_minutes = 0

    for business_hours_entry in store_business_hours:
        start_time_local = business_hours_entry.start_time_local
        end_time_local = business_hours_entry.end_time_local
        uptime_minutes += (end_time_local.hour - start_time_local.hour) * 60

    return uptime_minutes