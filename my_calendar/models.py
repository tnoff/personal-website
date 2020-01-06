from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=2048)

    def __str__(self):
        return self.name


class Birthday(models.Model):
    month = models.IntegerField()
    day = models.IntegerField()
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s.%s' % (self.person_id, self.month, self.day)
