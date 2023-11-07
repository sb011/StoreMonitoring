# StoreMonitoring
The Restaurant Status Monitoring API is a backend service designed to help restaurant owners monitor the online status of their stores during business hours. The API tracks store activity and provides insights into periods of inactivity, enabling restaurant owners to understand how often their stores were offline in the past. This information helps restaurant owners improve their online presence and customer service.

# Tech stack
* Fast API

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
RETURN report_id
```

2. Get a report
```
GET /get_report/{report_id}
RETURN CSV
```

# Logic of generating a report
* Get all the store IDs, business hours, store status, and timezones
* Iterate through every store ID and pass only the business hours, store status, and timezone which are for that particular store
  * downtime_last_hour
    * Get the current time for the store's local time
    * Get the last hour from the current time
    * Iterate through store status
      * check if the status is inactive
        * convert the timestamp_utc to local
        * Iterate through business hours
          * check if the day of the week is the same for the status and business hours
            * get the start and end time of the business hours and convert it to local time
            * case 1: last_hour_local is in working hours and current_time_local is in working hours
              * find the next active status which is between the last hour and add the minutes to the downtime
              * else add all the minutes from status local time to last hour end
            * case 2: last_hour_local is in working hours and current_time_local is not in working hours
              * find the next active status which is between the last hour and the end of working hours and add the minutes to the downtime
              * else add all the minutes from status local time to last hour end
  * downtime_last_day
    * Get the current time for the store's local time
    * Get the last day from the current time
    * Iterate through store status
      * check if the status is inactive
        * convert the timestamp_utc to local
        * Iterate through business hours
          * case 1: status_timestamp_local is in working hours count the minutes from the timestamp to the next active status which should be less than end_local and greater than start_local
            * find the next active status which is between the last day working hour and add the minutes to the downtime
            * else add all the minutes from status local time to last hour end
  * downtime_last_week
    * Get the current time for the store's local time
    * Get the last week from the current time
    * Iterate through store status
      * check if the status is inactive
        * convert the timestamp_utc to local
        * Iterate through business hours
          * case 1: status_timestamp_local is in working hours and count the minutes from the timestamp to next active status which should be less than end_local and greater than start_local
            * find the next active status which is between the last weeks business hour and add the minutes to the downtime
            * else add all the minutes from status local time to last hour end
  * uptime_last_hour
    * Get the current time for the store's local time
    * Get the last week from the current time
    * Iterate through business hours
      * check if the day of week is the same for the business hours and last hour
        * case1: one_hour_ago_local is in working hours and current_time_local is in working hours
        * case2: one_hour_ago_local is in working hours and current_time_local is not in working hours
        * case3: one_hour_ago_local is not in working hours and current_time_local is in working hours
        * case4: one_hour_ago_local is not in working hours and current_time_local is not in working hours
    * subtract from uptime_last_hour to downtime_last_hour
  * uptime_last_day
    * Get the current time for the store's local time
    * Get the last week from the current time
    * Iterate through business hours
      * check if the day of week is the same for the business hours and last day
        * add all the time from end business hour to start business hour
  * uptime_last_week
    * Get the current time for the store's local time
    * Get the last week from the current time
    * Iterate through business hours
      * add all the time from end business hour to start business hour
  
