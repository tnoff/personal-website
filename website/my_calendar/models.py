from django.db import models
from django.contrib.auth.models import User

from timezone_field import TimeZoneField

# https://stackoverflow.com/questions/2886987/adding-custom-fields-to-users-in-django
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-django-s-default-user
class WebsiteUserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = TimeZoneField(default='America/Los_Angeles')

class Group(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    birthday = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    groups = models.ManyToManyField(Group)

    def __str__(self):
        return self.name


class Task(models.Model):
    month_offset = models.IntegerField(blank=False, null=False)
    week_offset = models.IntegerField(blank=False, null=False)
    day_of_week = models.IntegerField(blank=False, null=False)
    message = models.CharField(max_length=255, blank=False, null=False)
    due_date = models.DateField(blank=False, null=False)

    def __str__(self):
        return self.message
