from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from my_calendar.constants import MONTHS
from my_calendar.models import Birthday

@login_required
def birthdays(request):
    birthdays = Birthday.objects.all()
    now = datetime.now()

    # Fix up data a bit
    for birthday in birthdays:
        # Get time delta
        birthday_datetime = datetime(now.year, birthday.month, birthday.day)
        birthday.delta = (birthday_datetime - now)
        # If delta negative, then day has past, so change to next year
        if birthday.delta.days < 0:
            birthday_datetime = datetime(now.year + 1, birthday.month, birthday.day)
            birthday.delta = (birthday_datetime - now)
        # Use readable month
        birthday.month = MONTHS[birthday.month - 1][1]

    # Sort by datetime delta
    birthdays = sorted(birthdays, key=lambda k: k.delta)
    # Generate output for view
    view_data = {
        'birthdays' : birthdays,
    }
    return render(request, 'my_calendar/birthdays.html', view_data)
