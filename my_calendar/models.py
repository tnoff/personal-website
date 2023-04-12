from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy

from timezone_field import TimeZoneField

# https://stackoverflow.com/questions/2886987/adding-custom-fields-to-users-in-django
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-django-s-default-user
class UserSettings(models.Model):
    '''
    Set timezone for user
    '''
    class Meta:
        verbose_name_plural = gettext_lazy("UserSettings")

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = TimeZoneField(default='America/Los_Angeles')
    week_start_day = models.IntegerField(default=0)
    birthdays_last_updated = models.DateTimeField()

    def __str__(self):
        return self.user.username #pylint:disable=no-member

class Group(models.Model):
    '''
    Group for Persons
    '''
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'

class Person(models.Model):
    '''
    Person for numbers and birthdays
    '''
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    birthday = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    groups = models.ManyToManyField(Group)

    def __str__(self):
        return f'{self.name}'

class Task(models.Model):
    '''
    Repeating Task
    '''
    month_offset = models.IntegerField(blank=False, null=False)
    week_offset = models.IntegerField(blank=False, null=False)
    day_of_week = models.IntegerField(blank=False, null=False)
    message = models.CharField(max_length=255, blank=False, null=False)
    due_date = models.DateField(blank=False, null=False)

    def __str__(self):
        return f'{self.message}'

class Event(models.Model):
    '''
    Single Events
    '''
    title = models.CharField(max_length=64, null=False, blank=False)
    description = models.TextField(blank=False, null=False)
    start = models.DateTimeField(blank=False, null=False)
    end = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return f'{self.title}'
