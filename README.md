# StoreMonitoring
The Restaurant Status Monitoring API is a backend service designed to help restaurant owners monitor the online status of their stores during business hours. The API tracks store activity and provides insights into periods of inactivity, enabling restaurant owners to understand how often their stores were offline in the past. This information helps restaurant owners improve their online presence and customer service.

# Tech stack
* Fast API

# Local Setup
1. Git clone
```
git clone https://github.com/sb011/StoreMonitoring.git
```
2. Make an environment
```
python -m venv env
```
3. Use that environment
```
.\env\Scripts\activate
```
4. Install the requirements
```
pip install -r requirements.txt
```

# Data dump
* Created the notebook and added the script to dump data into the database, including the database connection, table creation, and data inserting into tables.

# Data sources
1. Restaurant status
`store_id, timestamp_utc, status`
2. Business hours
`store_id, dayOfWeek(0=Monday, 6=Sunday), start_time_local, end_time_local`
3. Timezone
`store_id, timezone_str`

* Data output
`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)`

# End point
1. Trigger Report
```
POST /trigger_report
RETURN { report_id: <REPORTID> }
```

2. Get a report
```
GET /get_report/{report_id}
RETURN { status: <STATUS>, url: <URL>}
```

# Functionalities
* Multithreading
* File Upload

# Additional Enhancements (if I had more time)
* Add caching
* More optimize the report generation and make it faster

# Video
[Video](https://www.loom.com/share/ea88a16c16df45f68b90c6b6b0d812a8?sid=911b01fe-cad3-49e4-b7b5-45fc2bd3fd68)

# Logic of generating a report
1. Downtime for the last hour
   1. Find Current and Last Hour:
      * Determine the start of the current hour and the start of the last hour.
   2. Check Store Status:
      * Look at whether the store was inactive during the last hour.
   3. Calculate Downtime:
      * If the store was inactive and became active again within the last hour, calculate the downtime between the inactive and active periods.
      * If the store remained inactive until the current time, calculate the downtime up to the current time.
   4. Ensure Non-Negative Downtime:
      * Ensure the calculated downtime is a non-negative value (cannot be less than zero).
   5. Return Downtime:
      * Provide the duration of store inactivity during the last hour, in minutes.
      
2. Downtime for the last day
   1. Find Current and Last Day's Start Time:
      * Determine the start of the current day and the start of the previous day.
   2. Check Store Status:
      * Look at whether the store was inactive during the last day.
   3. Calculate Downtime:
      * If the store was inactive and became active again within the last day, calculate the downtime between the inactive and active periods.
      * If the store remained inactive until the current time, calculate the downtime up to the current time.
   4. Ensure Non-Negative Downtime:
      * Make sure the calculated downtime is non-negative (cannot be less than zero).
   5. Return Downtime:
      * Provide the duration of store inactivity during the last day, in minutes.
     
3. Downtime for the last week
   1. Check Store Status for the Last Week:
      * Look at the store's status records for the entire last week.
   2. Identify Inactive Periods:
      * If a status entry indicates that the store was inactive (status is 'inactive') and the inactive period falls within the last week, proceed to calculate downtime.
      * Compare the inactive status timestamp with the working hours of the same day to ensure it occurred during operational hours.
   3. Find Next Active Status Within Working Hours:
      * Look for the next 'active' status entry that occurred within the same working day and during operational hours, following the inactive period. This helps identify when the store became active again.
   4. Calculate Downtime Duration:
      * If a next active status entry is found, calculate the downtime duration between the inactive status and the next active status.
      * If no active status is found, indicating the store remained inactive until the end of working hours, calculate the downtime duration from the inactive status to the end of the working hours.
   5. Convert Downtime to Minutes:
      * Convert the calculated downtime duration from seconds to minutes by dividing it by 60.
   6. Ensure Non-Negative Downtime:
      * Ensure that the calculated downtime is non-negative. If it is negative (which should not happen), set it to zero.
   7. Return Downtime Duration:
      * The function returns the calculated downtime duration in minutes, representing the total time the store was inactive during the last week within its operational hours.
     
4. Uptime for the last hour
   1. Find Current and Last Hour's Time:
      * Determine the start of the current hour and the start of the last hour in the specified timezone.
   2. Check Store's Operational Hours:
      * Look at the store's defined operational hours for the specific day of the week corresponding to the last hour.
   3. Calculate Uptime:
      * If the last hour falls within the store's operational hours:
        * If the store was operational for the entire last hour, add 60 minutes to the uptime.
        * If the store was operational for part of the last hour, calculate the duration of uptime from the start of the last hour to the end of the operational period within that hour.
   4. Ensure Non-Negative Uptime:
      * Ensure that the calculated uptime is non-negative. If it is negative (which should not happen), set it to zero.
   5. Return Uptime Duration:
      * The function returns the calculated uptime duration in minutes, representing the total time the store was operational during the last hour.
        
5. Uptime for the last day
   1. Find Current Day's Start Time and Start of the Last Day:
      * Determine the start of the current day (midnight) and the start of the previous day (last day) in the specified timezone.
   2. Check Store's Operational Hours for the Last Day:
      * Look at the store's defined operational hours for the specific day of the week corresponding to the last day.
   3. Calculate Total Uptime:
      * For each set of operational hours on the last day, calculate the duration of uptime by subtracting the start time from the end time within each operational period.
      * Sum up the individual uptime durations from all operational periods to get the total uptime for the last day.
   4. Return Uptime Duration:
      * The function returns the calculated uptime duration in minutes, representing the total time the store was operational during the last day.
        
6. Uptime for the last week
   1. Loop Through Each Day of the Week:
      * For each day of the week in the last week:
   2. Calculate Daily Uptime:
      * Take the difference between the end time and start time of the store's operational hours on that day.
      * Multiply this difference by 60 to convert it from hours to minutes.
   3. Sum Up Daily Uptime:
      * Add up the calculated daily uptimes for all days of the last week.
   4. Return Total Uptime Duration:
      * The function returns the total uptime duration in minutes, representing the combined time the store was operational during each day of the last week.
