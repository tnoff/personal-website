from datetime import date, datetime, timedelta

from django.test import TestCase

from my_calendar.models import Task
from my_calendar.views import _find_next_due_date

class MyCalendarTestCase(TestCase):
    def test_tasks_due_date_weekly_past_due(self):
        # With a task due last sunday, make sure marking complete
        # with only a two week offset has correct timedelta
        last_sunday = date.today()
        while last_sunday.weekday() != 6:
            last_sunday -= timedelta(1)
        task = Task.objects.create(message="test message",
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=0,
                                   due_date=last_sunday)
        _find_next_due_date(task, date.today())
        time_delta = task.due_date - last_sunday
        self.assertEqual(time_delta.days, 14)

    def test_tasks_due_date_weekly_not_due(self):
        # With a task due next sunday, make sure marking complete
        # with only a two week offset has correct timedelta
        next_sunday = date.today()
        while next_sunday.weekday() != 6:
            next_sunday += timedelta(1)
        task = Task.objects.create(message="test message",
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=0,
                                   due_date=next_sunday)
        _find_next_due_date(task, task.due_date + timedelta(1))
        time_delta = task.due_date - next_sunday
        self.assertEqual(time_delta.days, 14)

    def test_tasks_due_date_monthly_paste_due(self):
        # With a task due last sunday, make sure marking complete
        # with a month offset has correct dimensions
        last_sunday = date.today()
        while last_sunday.weekday() != 6:
            last_sunday -= timedelta(1)
        task = Task.objects.create(message="test message",
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=1,
                                   due_date=last_sunday)
        _find_next_due_date(task, date.today())
        # Make sure due date is second sunday of month
        self.assertEqual((task.due_date - timedelta(7)).month, task.due_date.month)
        self.assertNotEqual((task.due_date - timedelta(14)).month, task.due_date.month)
