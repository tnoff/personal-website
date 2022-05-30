from datetime import date, datetime, timedelta

import pytz

def get_time_with_leading_zeros(datetime_obj):
    '''
    Get HH:MM with leading zeros
    '''
    time_string = ''
    if datetime_obj.hour < 10:
        time_string = f'{time_string}0'
    time_string = f'{time_string}{datetime_obj.hour}:'
    if datetime_obj.minute < 10:
        time_string = f'{time_string}0'
    time_string = f'{time_string}{datetime_obj.minute}'
    return time_string

def find_next_due_date(month_offset, week_offset, day_of_week, start, due_date=None):
    '''
    Find next due date for a task

    month_offset (int)   :   Month offset
    week_offset  (int)   :   Week offset
    day_of_week  (int)   :   Day of week
    start        (date)  :   Find next due date after this start date
    due_date     (date)  :   Existing due date, if any
    '''
    if due_date is None:
        due_date = start - timedelta(days=7)
    time_delta = due_date - start
    # If task is not done, then it is overdue
    while time_delta.days < 0:
        # First add month offset
        next_year = due_date.year
        next_month = due_date.month + month_offset
        if next_month > 12:
            next_year += 1
            next_month -= 12

        # Use start date of 1 if new month
        if due_date.month != next_month:
            due_date = date(next_year, next_month, 1)
        # Else just add one to date
        else:
            due_date += timedelta(1)
        # Go to first day that matches week day
        while due_date.weekday() != day_of_week:
            due_date += timedelta(1)
        # Now add proper week offset
        due_date += timedelta(7 * (week_offset - 1))
        # Check again if before todays date
        time_delta = due_date - start
    return due_date

def get_today_with_timezone(zone):
    '''
    Get current date within timezone
    '''
    return datetime.now(pytz.timezone(zone)).date()
