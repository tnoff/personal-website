from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from my_calendar.constants import MONTHS
from my_calendar.models import Person, Task

@login_required
def birthdays(request):
    today = date.today()
    persons = Person.objects.order_by('birthday')

    append_last = []
    person_list = []
    for person in persons:
        if person.birthday < today:
            person.birthday = date(today.year + 1, person.birthday.month, person.birthday.day)
            person.save()
        person.delta = person.birthday - today
        person.birthday_string = person.birthday.strftime("%B %d")
        person_list.append(person)

    person_list += append_last

    view_data = {
        'persons' : person_list,
    }
    return render(request, 'my_calendar/birthdays.html', view_data)

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
