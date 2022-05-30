'''
We keep persons birthdays as a single date to show
This means that once a bday has past, we should bump up the date by a year so it shows
'''
from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from my_calendar.models import Person

class Command(BaseCommand):
    help = 'Update birthdays to switch to next year'

    def add_arguments(self, parser):
        parser.add_argument('--time-delta', type=int, default=60)

    def handle(self, *args, **options):
        today = date.today()
        past_bdays = Person.objects.filter(birthday__lt=(today - timedelta(options['time_delta']))) #pylint:disable=no-member
        for person in past_bdays:
            person.birthday = date(today.year + 1, person.birthday.month, person.birthday.day)
            person.save()
            self.stdout.write(self.style.SUCCESS(f'Updated person birthday "{person.name}"'))