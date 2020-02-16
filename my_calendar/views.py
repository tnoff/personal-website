from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.models import Person, Task

def _update_past_birthdays(today=None):
    if today is None:
        today = date.today()
    past_bdays = Person.objects.filter(birthday__lt=today)
    for person in past_bdays:
        person.birthday = date(today.year + 1, person.birthday.month, person.birthday.day)
        person.save()

def _find_next_due_date(task, start):
    task.time_delta = task.due_date - start
    # If task is not done, then it is overdue
    while task.time_delta.days < 0:
        # First add month offset
        next_year = task.due_date.year
        next_month = task.due_date.month + task.month_offset
        if next_month > 12:
            next_year += 1
            next_month -= 12

        # Use start date of 1 if new month
        if task.due_date.month != next_month:
            task.due_date = date(next_year, next_month, 1)
        # Else just add one to date
        else:
            task.due_date += timedelta(1)
        # Go to first day that matches week day
        while task.due_date.weekday() != task.day_of_week:
            task.due_date += timedelta(1)
        # Now add proper week offset
        task.due_date += timedelta(7 * (task.week_offset - 1))
        # Check again if before todays date
        task.time_delta = task.due_date - start


class Day():
    def __init__(self, datetime_date, today):
        self.number = datetime_date.day
        self.is_today = (datetime_date == today)
        self.birthdays = [item.name for item in Person.objects.filter(birthday=datetime_date)]
        self.tasks = [item.message for item in Task.objects.filter(due_date=datetime_date)]


@login_required
def birthdays(request):
    today = date.today()
    _update_past_birthdays(today=today)
    persons = Person.objects.order_by('birthday')

    append_last = []
    person_list = []
    for person in persons:
        person.delta = person.birthday - today
        person.birthday_string = person.birthday.strftime("%B %d")
        person_list.append(person)

    person_list += append_last

    view_data = {
        'persons' : person_list,
    }
    return render(request, 'my_calendar/birthdays.html', view_data)

@login_required
def tasks(request):
    now = date.today()
    tasks = Task.objects.all()
    for task in tasks:
        task.time_delta = task.due_date - now
        task.due_date = task.due_date.strftime("%B %d")
    # Sort by time delta
    tasks = sorted(tasks, key=lambda k: k.time_delta)
    view_data = {
        'tasks' : tasks
    }
    return render(request, 'my_calendar/tasks.html', view_data)

@login_required
def task_mark_done(request, task_id):
    now = date.today()
    task = Task.objects.get(id=task_id)
    # If past due date, use today
    if task.due_date < now:
         _find_next_due_date(task, now)
    # If due date in future, use due date to calculate
    else:
        _find_next_due_date(task, task.due_date + timedelta(1))
    task.save()
    return redirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8')

@login_required
def calendar(request, year=None, month=None):
    # Get date from defaults
    today = date.today()
    _update_past_birthdays(today=today)
    try:
        year = int(year)
    except TypeError:
        year = today.year
    try:
        month = int(month)
    except TypeError:
        month = today.month

    # Figure out next month, previous month
    next_month = month + 1
    next_year = year
    prev_month = month - 1
    prev_year = year
    if next_month == 13:
        next_year += 1
        next_month = 1
    if prev_month == 0:
        prev_year -= 1
        prev_month = 12

    # Get days of week names
    days_of_week_names = [day[1] for day in DAYS_OF_WEEK]

    # List of weeks for table rows
    week_table_rows = []
    week_row = []

    # Add empty nodes for first week, so first row starts on first day
    datetime_day = date(year, month, 1)
    for _ in range(datetime_day.weekday()):
        week_row.append(None)
    # Iterate through all month days
    while datetime_day.month == month:
        day_object = Day(datetime_day, today)
        week_row.append(day_object)
        if datetime_day.weekday() == 6:
            week_table_rows.append(week_row)
            week_row = []
        datetime_day += timedelta(1)
    # Check for remaining days, add empty nodes
    if week_row:
        for _ in range(7 - datetime_day.weekday()):
            week_row.append(None)
        week_table_rows.append(week_row)



    # Construct all variables
    view_data = {
        'calendar_name' : '%s %s' % (MONTHS[month - 1][1], year),
        'next_month' : '%s/%s' % (next_year, next_month),
        'prev_month' : '%s/%s' % (prev_year, prev_month),
        'days_of_week_names' : days_of_week_names,
        'week_table_rows' : week_table_rows,
    }
    return render(request, 'my_calendar/calendar.html', view_data)
