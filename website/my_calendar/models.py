from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    birthday = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)

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
