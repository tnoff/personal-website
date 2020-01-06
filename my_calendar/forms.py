from django import forms

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.models import Birthday, Task

class BirthdayForm(forms.ModelForm):
    month = forms.ChoiceField(choices = MONTHS)

    class Meta:
        model = Birthday
        fields = '__all__'

    def clean_month(self):
        month = int(self.cleaned_data['month'])
        if not month:
            raise forms.ValidationError("Month value required")
        if month < 1 or month > 12:
            raise forms.ValidationError("Invalid month value %s" % month)
        return month

    def clean_day(self):
        day = int(self.cleaned_data['day'])
        month = int(self.cleaned_data['month'])
        if not day:
            raise forms.ValidationError("Day value required")
        if day < 1:
            raise forms.ValidationError("Day must be positive integer")
        if month == 2:
            if day > 29:
                raise forms.ValidationError("Invalid day %s for month 2" % day)
        elif month in [4, 6, 9, 11]:
            if day > 30:
                raise forms.ValidationError("Invalid day %s for month %s" % (day, month))
        else:
            if day > 31:
                raise forms.ValidationError("Invalid day %s for month %s" % (day, month))
        return day

    def clean_person(self):
        person = self.cleaned_data['person']

        existing_birthdays = Birthday.objects.filter(person=person.id)
        if existing_birthdays:
            raise forms.ValidationError("Person %s already has a birthday on record" % person)
        return person

class TaskForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(choices = DAYS_OF_WEEK)

    class Meta:
        model = Task
        fields = '__all__'

    def clean_month_offset(self):
        month_offset = int(self.cleaned_data['month_offset'])
        if month_offset < 1:
            raise forms.ValidationError("Month offset must be positive integer")
        if month_offset > 6:
            raise forms.ValidationError("Month offset cannot be greater than 6")
        return month_offset

    def clean_week_offset(self):
        week_offset = int(self.cleaned_data['week_offset'])
        if week_offset < 1:
            raise forms.ValidationError("Week offset must be positive integer")
        if week_offset > 4:
            raise forms.ValidationError("Week offset cannot be greater than 4")
        return week_offset
