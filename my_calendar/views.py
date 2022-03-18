from copy import deepcopy
from datetime import date, datetime, timedelta

import pytz

from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django_otp.decorators import otp_required

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.forms import EventForm, GroupForm, PersonForm, TaskForm
from my_calendar.models import Event, Group, Person, Task
from my_calendar.utils import get_today_with_timezone
from my_calendar.utils import get_time_view, find_next_due_date, get_time_with_leading_zeros

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
        now = get_today_with_timezone(request.user.usersettings.timezone.zone)
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
    try:
        now = get_today_with_timezone(request.user.usersettings.timezone.zone)
    except AttributeError:
        now = date.today()
    view_data = {
        'operation': 'create',
        'days_of_week': DAYS_OF_WEEK,
        'week_offset_display': [num for num in range(1, 5)],
        'month_offset_display': [num for num in range(7)],
        'default_due_date': now.strftime('%Y-%m-%d'),
    }
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
        view_data['errors'] = form.errors
        return render(request, 'my_calendar/task.html', view_data)
    return render(request, 'my_calendar/task.html', view_data)

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
def task_update(request, task_id):
    '''
    Update individual task
    '''
    task = Task.objects.get(id=task_id) #pylint:disable=no-member
    if not task:
        raise Http404(f'Unable to locate task id: {task_id}')

    view_data = {
        'task': task,
        'operation': 'update',
        'days_of_week': DAYS_OF_WEEK,
        'week_offset_display': [num for num in range(1, 5)],
        'month_offset_display': [num for num in range(7)],
        'default_due_date': task.due_date.strftime('%Y-%m-%d'),
    }

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            for key, value in form.data.items():
                if key == 'csrfmiddlewaretoken':
                    continue
                setattr(task, key, value)
            task.save()
            return HttpResponseRedirect('/0d27c6b9-a5d7-4782-9438-93b54b8f98f8/')
        view_data['errors'] = form.errors
        return render(request, 'my_calendar/task.html', view_data)
    return render(request, 'my_calendar/task.html', view_data)

@otp_required
def task_mark_done(request, task_id):
    '''
    API call to mark task as done
    '''
    try:
        now = get_today_with_timezone(request.user.usersettings.timezone.zone)
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
def person_create(request):
    '''
    Create new person
    '''
    return _generate_person(request, None, 'create')

@otp_required
def person_update(request, person_id):
    '''
    Update existing person
    '''
    person = Person.objects.get(id=person_id) #pylint:disable=no-member
    if not person:
        raise Http404(f'Unable to locate person id: {person_id}')
    return _generate_person(request, person, 'update')

def _generate_person(request, person, operation):
    if person:
        # Set non values to blank strings for form
        if not person.phone_number:
            person.phone_number = ''
        if not person.birthday:
            person.birthday = ''

        # Make sure birthday in proper form format
        if person.birthday:
            person.birthday = person.birthday.strftime('%Y-%m-%d')
        # Get group ids for form
        person.group_ids = [group.id for group in person.groups.all()]

    view_data = {
        'operation': operation,
        'person': person,
        'possible_groups': [(group.id, group.name) for group in Group.objects.all()], #pylint:disable=no-member
    }
    if request.method == 'POST':
        groups = [int(group) for group in request.POST.getlist('groups')] or []
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save()
            person.groups.set(groups)
            person.save()
            return HttpResponseRedirect('/e37047af-f536-423e-8a72-731cbced13ea/')
        view_data['errors'] = form.errors
        return render(request, 'my_calendar/person.html', view_data)
    return render(request, 'my_calendar/person.html', view_data)

@otp_required
def person_delete(_request, person_id):
    '''
    Delete individual person
    '''
    person = Person.objects.get(id=person_id) #pylint:disable=no-member
    if not person:
        raise Http404(f'Unable to locate person id:{person_id}')

    person.delete()
    return HttpResponseRedirect('/e37047af-f536-423e-8a72-731cbced13ea/')

@otp_required
def people_list(request):
    '''
    Show all persons with phone numbers and birthdays
    '''
    page_number = request.GET.get('page')

    # Only show given groups
    groups = request.GET.get('groups', '')
    if groups:
        groups = groups.split(',')

    try:
        today = get_today_with_timezone(request.user.usersettings.timezone.zone)
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

    people = people.order_by(Lower('name'))

    # Limit 25 results per page
    paginator = Paginator(people, 25)
    people = paginator.get_page(page_number)

    for person in people:
        person.group_names = [group.name for group in person.groups.all()]
        if person.phone_number:
            phone_number_string = '%s (%s) %s-%s' % (person.phone_number[:-10],
                                                     person.phone_number[-10:-7],
                                                     person.phone_number[-7:-4],
                                                     person.phone_number[-4:])
            person.phone_number = phone_number_string
        if person.birthday:
            person.birthday = person.birthday.strftime('%B %d')

    # Groups suffix for page links
    if groups:
        groups = f'&groups={",".join(group for group in groups)}'
    else:
        groups = ''

    view_data = {
        'people' : people,
        'groups': groups,
    }
    return render(request, 'my_calendar/people_list.html', view_data)

#
# Group Methods
#

# TODO add proper group edit/delete

@otp_required
def group_create(request):
    '''
    Create new Group
    '''
    view_data = {
        'operation': 'create',
        'possible_people': [(person.id, person.name) for person in Person.objects.all()], #pylint:disable=no-member
    }
    if request.method == 'POST':
        people = [int(person) for person in request.POST.getlist('people')] or []
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            for person in people:
                person = Person.objects.get(id=person) #pylint:disable=no-member
                person.groups.add(group)
                person.save()
            return HttpResponseRedirect('/e37047af-f536-423e-8a72-731cbced13ea/'\
                                        f'?groups={group.name}')
        view_data['errors'] = form.errors
        return render(request, 'my_calendar/group.html', view_data)
    return render(request, 'my_calendar/group.html', view_data)


#
# Event Method
#

@otp_required
def event_update(request, event_id):
    '''
    Show full info for given event
    '''
    event = Event.objects.get(pk=event_id) #pylint:disable=no-member
    if not event:
        raise Http404(f'Unable to locate event id: {event_id}')
    return _generate_event(request, event, 'update')

@otp_required
def event_create(request):
    '''
    Create new event
    '''
    return _generate_event(request, None, 'create')

def _generate_event(request, event, operation):
    view_data = {
        'event': event,
        'operation': 'update',
    }
    try:
        timezone = pytz.timezone(request.user.usersettings.timezone.zone)
        now = get_today_with_timezone(request.user.usersettings.timezone.zone)
    except AttributeError:
        timezone = pytz.utc
        now = date.today()

    view_data = {
        'event': event,
        'operation': operation,
        'default_date': now.strftime('%Y-%m-%d'),
    }

    if request.method == 'POST':
        # We do not have the proper datetime objects from the form
        # So here we need to generate the datetime objects from the date, and then time
        form_data = dict(request.POST)
        form_data['title'] = form_data.pop('title')[0]
        form_data['description'] = form_data.pop('description')[0]
        event_date = datetime.strptime(form_data.pop('event_date')[0], '%Y-%m-%d')
        event_start_time = datetime.strptime(form_data.pop('start_time')[0], '%H:%M')
        event_end_time = datetime.strptime(form_data.pop('end_time')[0], '%H:%M')

        local_start = datetime(event_date.year, event_date.month, event_date.day,
                               event_start_time.hour, event_start_time.minute)
        local_end = datetime(event_date.year, event_date.month, event_date.day,
                             event_end_time.hour, event_end_time.minute)

        form_data['start'] = timezone.localize(local_start, is_dst=None).astimezone(pytz.utc)
        form_data['end'] = timezone.localize(local_end, is_dst=None).astimezone(pytz.utc)

        form = EventForm(form_data, instance=event)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/{form.data["start"].year}/{form.data["start"].month}')
        view_data['errors'] = form.errors

    if operation == 'update':
        try:
            event.start = event.start.astimezone(timezone)
            event.end = event.end.astimezone(timezone)
            event.date = event.start.strftime('%Y-%m-%d')
            event.start_string = get_time_with_leading_zeros(event.start)
            event.end_string = get_time_with_leading_zeros(event.end)
        except AttributeError:
            pass

    return render(request, 'my_calendar/event.html', view_data)

@otp_required
def event_delete(request, event_id):
    '''
    Delete given event
    '''
    event = Event.objects.get(pk=event_id) #pylint:disable=no-member
    if not event:
        raise Http404(f'Unable to locate event id: {event_id}')
    event.delete()
    return HttpResponseRedirect('/5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/')

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
        # Grab next day in case timezones go over
        day_events = Event.objects.filter(start__range=[datetime_date - timedelta(days=2), #pylint:disable=no-member
                                                        datetime_date + timedelta(days=2)]).order_by('start')
        for item in day_events:
            if timezone:
                item.start = item.start.astimezone(timezone)
                item.end = item.end.astimezone(timezone)
            # Check if day matches, for timezones
            if item.start.day != datetime_date.day:
                continue
            item.time_string = f'{item.start.strftime("%H:%M")}-{item.end.strftime("%H:%M")}'
            self.events.append(item)

@otp_required
def calendar(request, year=None, month=None): #pylint:disable=too-many-locals
    '''
    Calednar view with birthdays and tasks
    '''
    # Get date from defaults
    try:
        timezone = pytz.timezone(request.user.usersettings.timezone.zone)
        today = get_today_with_timezone(request.user.usersettings.timezone.zone)
    except AttributeError:
        timezone = None
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

    # Rotate to start of week for user
    days_of_week_names = [day[1] for day in DAYS_OF_WEEK]
    for _ in range(request.user.usersettings.week_start_day):
        days_of_week_names.append(days_of_week_names.pop(0))
    
    # End of week day, for rotating later
    end_of_week_day = request.user.usersettings.week_start_day - 1
    if end_of_week_day < 0:
        end_of_week_day = 6


    # List of weeks for table rows
    week_table_rows = []
    week_row = []

    datetime_day = date(year, month, 1)
    # Start with beginning of week, even if previous month
    while datetime_day.weekday() != request.user.usersettings.week_start_day:
        datetime_day = datetime_day - timedelta(1)

    # End of month
    try:
        end_day = date(year, month + 1, 1) - timedelta(days=1)
    except ValueError:
        # Assume next year
        end_day = date(year + 1, 1, 1) - timedelta(days=1)

    # Iterate through all month days
    while datetime_day <= end_day:
        day_object = Day(datetime_day, today, timezone=timezone)
        week_row.append(day_object)
        if datetime_day.weekday() == end_of_week_day:
            week_table_rows.append(week_row)
            week_row = []
        datetime_day += timedelta(1)
    # Add remaining days in week, even if next month
    if week_row:
        while day_object.datetime_date.weekday() != end_of_week_day:
            day_object = Day(datetime_day, today, timezone=timezone)
            week_row.append(day_object)
            datetime_day += timedelta(1)
        week_table_rows.append(week_row)

    # Construct all variables
    view_data = {
        'calendar_name' : f'{MONTHS[month - 1][1]} {year}',
        'next_month' : f'{next_year}/{next_month}',
        'prev_month' : f'{prev_year}/{prev_month}',
        'days_of_week_names' : days_of_week_names,
        'week_table_rows' : week_table_rows,
    }
    return render(request, 'my_calendar/calendar.html', view_data)
