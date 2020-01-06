from django import forms

from my_calendar.constants import MONTHS
from my_calendar.models import Birthday, Person

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
