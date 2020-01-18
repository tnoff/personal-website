from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Birthday(models.Model):
    month = models.IntegerField(blank=False, null=False)
    day = models.IntegerField(blank=False, null=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return '%s - %s.%s' % (self.person, self.month, self.day)

class Task(models.Model):
    month_offset = models.IntegerField(blank=False, null=False)
    week_offset = models.IntegerField(blank=False, null=False)
    day_of_week = models.IntegerField(blank=False, null=False)
    message = models.CharField(max_length=255, blank=False, null=False)
    due_date = models.DateField(blank=False, null=False)

    def __str__(self):
        return self.message
