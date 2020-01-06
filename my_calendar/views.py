from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from my_calendar.constants import MONTHS
from my_calendar.models import Birthday, Task

@login_required
def birthdays(request):
    # TODO change this to date
    now = datetime.now()
    birthdays = Birthday.objects.all()

    # Fix up data a bit
    for birthday in birthdays:
        # Get time delta
        birthday_datetime = datetime(now.year, birthday.month, birthday.day)
        birthday.delta = (birthday_datetime - now)
        # If delta negative, then day has past, so change to next year
        if birthday.delta.days < 0:
            birthday_datetime = datetime(now.year + 1, birthday.month, birthday.day)
            birthday.delta = (birthday_datetime - now)
        # Use readable month
        birthday.month = MONTHS[birthday.month - 1][1]

    # Sort by datetime delta
    birthdays = sorted(birthdays, key=lambda k: k.delta)
    # Generate output for view
    view_data = {
        'birthdays' : birthdays,
    }
    return render(request, 'my_calendar/birthdays.html', view_data)

def _find_next_due_date(task, start, force_future=False):
    task.next_due_date = task.due_date
    task.time_delta = task.next_due_date - start
    # If task is not done, then it is overdue
    while task.time_delta.days < 0 and (task.marked_done or force_future):
        # First add month offset
        next_year = task.due_date.year
        next_month = task.due_date.month + task.month_offset
        if next_month > 12:
            next_year += 1
            next_month -= 12
        # Use start date of 1
        task.next_due_date = date(next_year, next_month, 1)
        # Go to first day that matches week day
        while task.next_due_date.weekday() != task.day_of_week:
            task.next_due_date += timedelta(1)
        # Now add proper week offset
        task.next_due_date += timedelta(7 * (task.week_offset - 1))
        # Check again if before todays date
        task.time_delta = task.next_due_date - start

@login_required
def tasks(request):
    now = date.today()
    tasks = Task.objects.all()
    for task in tasks:
        _find_next_due_date(task, now)
        task.due_date = task.next_due_date.strftime("%B %d")
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
    # First get current due date
    _find_next_due_date(task, now)
    # Then find next due date
    _find_next_due_date(task, task.next_due_date + timedelta(1), force_future=True)
    task.due_date = task.next_due_date
    task.marked_done = False
    task.save()
    return redirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8')
