from datetime import date, timedelta

import pytz

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django_otp.decorators import otp_required

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.forms import TaskForm
from my_calendar.models import Event, Person, Task
from my_calendar.utils import get_today_with_timezone
from my_calendar.utils import get_time_view, find_next_due_date

def _update_past_birthdays(today=None, delta=31):
    '''
    Today: Current date, can be passed in
    Delta: Offset when to rotate birthdays
    '''
    if today is None:
        today = date.today()
    past_bdays = Person.objects.filter(birthday__lt=(today - timedelta(delta))) #pylint:disable=no-member
    for person in past_bdays:
        person.birthday = date(today.year + 1, person.birthday.month, person.birthday.day)
        person.save()

#
# Task Methods
#


@otp_required
def task_list(request):
    '''
    Show tasks as a sorted list
    '''
    try:
        now = get_today_with_timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        now = date.today()
    tasks = Task.objects.all() #pylint:disable=no-member
    for task in tasks:
        task.time_delta = task.due_date - now
        task.due_date_no_year = task.due_date.strftime("%B %d")
    # Sort by time delta
    tasks = sorted(tasks, key=lambda k: k.time_delta)
    view_data = {
        'tasks' : tasks
    }
    return render(request, 'my_calendar/task_list.html', view_data)

@otp_required
def task_create(request):
    '''
    Create new task
    '''
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_data = {}
            for key, value in form.data.items():
                if key == 'csrfmiddlewaretoken':
                    continue
                task_data[key] = value
            new_task = Task(**task_data)
            new_task.save()
            return HttpResponseRedirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8/')
        return render(request, 'my_calendar/task_create.html',
                      {'errors': form.errors})
    return render(request, 'my_calendar/task_create.html')

@otp_required
def task_delete(_request, task_id):
    '''
    Delete individual task
    '''
    task = Task.objects.get(id=task_id) #pylint:disable=no-member
    if not task:
        raise Http404(f'Unable to locate task id:{task_id}')

    task.delete()
    return HttpResponseRedirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8/')


@otp_required
def task_show(request, task_id):
    '''
    Show individual task
    '''
    task = Task.objects.get(id=task_id) #pylint:disable=no-member
    if not task:
        raise Http404(f'Unable to locate task id: {task_id}')

    # If not delete show
    try:
        now = get_today_with_timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        now = date.today()
    task.time_delta = task.due_date - now
    if task.time_delta.days < -1:
        task.time_delta = f'{task.time_delta.days} days ago'
    elif task.time_delta.days == -1:
        task.time_delta = '1 day ago'
    elif task.time_delta.days == 0:
        task.time_delta = 'today'
    elif task.time_delta.days == 1:
        task.time_delta = 'tomorrow'
    else:
        task.time_delta = f'in {task.time_delta.days} days'
    task.due_date = task.due_date.strftime("%B %d")

    day_of_week = DAYS_OF_WEEK[task.day_of_week][1]

    # Show 1st, 2nd, 3rd, or Nth week offset
    if task.week_offset == 1:
        # If month offset is 0, this is every week
        if task.month_offset == 0:
            task.week_offset = ''
        else:
            task.week_offset = 'on the 1st'
    elif task.week_offset == 2:
        task.week_offset = 'on the 2nd'
    elif task.week_offset == 3:
        task.week_offset = 'one the 3rd'
    else:
        task.week_offset = f'one the {task.week_offset}th'

    # Show month, or multiple months
    if task.month_offset == 0:
        task.month_offset = ''
    elif task.month_offset == 1:
        task.month_offset = 'month,'
    else:
        task.month_offset = f'{task.month_offset} months,'

    view_data = {
        'task' : task,
        'day_of_week' : day_of_week,
    }
    return render(request, 'my_calendar/task_show.html', view_data)

@otp_required
def task_mark_done(request, task_id):
    '''
    API call to mark task as done
    '''
    try:
        now = get_today_with_timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        now = date.today()
    task = Task.objects.get(id=task_id) #pylint:disable=no-member
    if not task:
        raise Http404(f'Unable to locate task id: {task_id}')
    # If past due date, use today
    if task.due_date < now:
        task.due_date = find_next_due_date(task.month_offset,
                                           task.week_offset,
                                           task.day_of_week,
                                           now,
                                           due_date=task.due_date)
    # If due date in future, use due date to calculate
    else:
        task.due_date = find_next_due_date(task.month_offset,
                                           task.week_offset,
                                           task.day_of_week,
                                           task.due_date + timedelta(1),
                                           due_date=task.due_date)
    task.save()
    return redirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8')

#
# Person Methods
#

@otp_required
def persons(request):
    '''
    Show all persons with phone numbers and birthdays
    '''
    # Only show given groups
    groups = request.GET.get('groups', '')
    if groups:
        groups = groups.split(',')

    try:
        today = get_today_with_timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        today = date.today()
    _update_past_birthdays(today=today)

    # If no groups, get all people
    if not groups:
        people = Person.objects.all() #pylint:disable=no-member
    # Else iterate through all groups
    else:
        # Use first group to create first queryset
        people = Person.objects.filter(groups__name=groups[0]) #pylint:disable=no-member
        for group in groups[1:]:
            people = people | Person.objects.filter(groups__name=group) #pylint:disable=no-member


    birthday_persons = []
    past_birthdays = []
    no_birthdays = []
    for person in people.order_by('birthday'):
        person.group_names = [group.name for group in person.groups.all()]
        if person.birthday:
            person.birthday_string = person.birthday.strftime("%B %d")
            person.birthday_delta = (person.birthday - today).days
            # If delta is not negative add to list, else add to append list
            if (person.birthday - today).days < 0:
                birthday_next_year = date(person.birthday.year + 1,
                                          person.birthday.month,
                                          person.birthday.day)
                person.birthday_delta = (birthday_next_year - today).days
                past_birthdays.append(person)
            else:
                birthday_persons.append(person)
        else:
            # Keep this last so the folks with no bdays go in the append last list
            no_birthdays.append(person)
        if person.phone_number:
            phone_number_string = '%s (%s) %s-%s' % (person.phone_number[:-10],
                                                     person.phone_number[-10:-7],
                                                     person.phone_number[-7:-4],
                                                     person.phone_number[-4:])
            person.phone_number = phone_number_string

    person_list = birthday_persons + past_birthdays + no_birthdays

    view_data = {
        'persons' : person_list,
    }
    return render(request, 'my_calendar/persons.html', view_data)

#
# Event Method
#

@otp_required
def event_show(request, event_id):
    '''
    Show full info for given event
    '''
    event = Event.objects.get(pk=event_id) #pylint:disable=no-member
    if not event:
        raise Http404(f'Unable to locate event id: {event_id}')
    try:
        timezone = pytz.timezone(request.user.websiteusersettings.timezone.zone)
        event.start = event.start.astimezone(timezone)
        event.end = event.end.astimezone(timezone)
    except AttributeError:
        pass

    event = get_time_view(event)
    view_data = {
        'event': event,
    }

    return render(request, 'my_calendar/event_show.html', view_data)

#
# Calendar Display
#

class Day():
    '''
    Day object to keep trakc of birthdays and events per day
    '''
    def __init__(self, datetime_date, today, timezone=None):
        self.datetime_date = datetime_date
        self.is_today = datetime_date == today
        self.birthdays = [item.name for item in Person.objects.filter(birthday=datetime_date)] #pylint:disable=no-member
        self.tasks = Task.objects.filter(due_date=datetime_date) #pylint:disable=no-member
        self.events = []
        day_events = Event.objects.filter(start__range=[datetime_date, #pylint:disable=no-member
                                                        datetime_date + timedelta(days=1)])
        for item in day_events:
            if timezone:
                item.start = item.start.astimezone(timezone)
                item.end = item.end.astimezone(timezone)
            item = get_time_view(item)
            self.events.append(item)

@otp_required
def calendar(request, year=None, month=None):
    '''
    Calednar view with birthdays and tasks
    '''
    # Get date from defaults
    try:
        today = get_today_with_timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        today = date.today()
    _update_past_birthdays(today=today)
    try:
        timezone = pytz.timezone(request.user.websiteusersettings.timezone.zone)
    except AttributeError:
        timezone = None

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
        day_object = Day(datetime_day, today, timezone=timezone)
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
