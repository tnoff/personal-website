from datetime import date, timedelta

from django.test import TestCase

from my_calendar.models import Task
from my_calendar.utils import find_next_due_date

class TestTask(TestCase):
    '''
    Test task functions
    '''
    def test_tasks_due_date_weekly_past_due(self):
        '''
        With a task due last sunday, make sure marking complete
        with only a two week offset has correct timedelta
        Make sure to subtract one here in case today is sunday
        '''
        last_sunday = date.today() - timedelta(1)
        while last_sunday.weekday() != 6:
            last_sunday -= timedelta(1)
        task = Task.objects.create(message="test message", #pylint:disable=no-member
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=0,
                                   due_date=last_sunday)
        task.due_date = find_next_due_date(task.month_offset,
                                           task.week_offset,
                                           task.day_of_week,
                                           date.today(),
                                           due_date=task.due_date)
        time_delta = task.due_date - last_sunday
        self.assertEqual(time_delta.days, 14)

    def test_tasks_due_date_weekly_not_due(self):
        '''
        With a task due next sunday, make sure marking complete
        with only a two week offset has correct timedelta
        Make sure to add one here in case today is sunday
        '''
        next_sunday = date.today() + timedelta(1)
        while next_sunday.weekday() != 6:
            next_sunday += timedelta(1)
        task = Task.objects.create(message="test message", #pylint:disable=no-member
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=0,
                                   due_date=next_sunday)
        task.due_date = find_next_due_date(task.month_offset,
                                           task.week_offset,
                                           task.day_of_week,
                                           task.due_date + timedelta(1),
                                           due_date=task.due_date)
        time_delta = task.due_date - next_sunday
        self.assertEqual(time_delta.days, 14)

    def test_tasks_due_date_monthly_paste_due(self):
        '''
        With a task due last sunday, make sure marking complete
        with a month offset has correct dimensions
        Make sure to subtract one here in case today is sunday
        '''
        last_sunday = date.today() - timedelta(1)
        while last_sunday.weekday() != 6:
            last_sunday -= timedelta(1)
        task = Task.objects.create(message="test message", #pylint:disable=no-member
                                   day_of_week=6,
                                   week_offset=2,
                                   month_offset=1,
                                   due_date=last_sunday)
        task.due_date = find_next_due_date(task.month_offset,
                                           task.week_offset,
                                           task.day_of_week,
                                           date.today(),
                                           due_date=task.due_date)
        # Make sure due date is second sunday of month
        self.assertEqual((task.due_date - timedelta(7)).month, task.due_date.month)
        self.assertNotEqual((task.due_date - timedelta(14)).month, task.due_date.month)
