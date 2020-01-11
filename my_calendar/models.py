from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name


class Birthday(models.Model):
    month = models.IntegerField(null=False)
    day = models.IntegerField(null=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return '%s - %s.%s' % (self.person, self.month, self.day)

class Task(models.Model):
    month_offset = models.IntegerField(null=False)
    week_offset = models.IntegerField(null=False)
    day_of_week = models.IntegerField(null=False)
    message = models.CharField(max_length=1024, null=False)
    due_date = models.DateField(blank=False)

    def __str__(self):
        return self.message
