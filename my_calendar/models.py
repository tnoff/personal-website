from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Birthday(models.Model):
    month = models.IntegerField()
    day = models.IntegerField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s.%s' % (self.person, self.month, self.day)

class Task(models.Model):
    month_offset = models.IntegerField()
    week_offset = models.IntegerField()
    day_of_week = models.IntegerField()
    message = models.CharField(max_length=1024)
    due_date = models.DateField(blank=False)
    marked_done = models.BooleanField(default=False)

    def __str__(self):
        return self.message
