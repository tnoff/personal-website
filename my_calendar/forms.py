import re

from django import forms

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.models import Person, Task

# https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
PHONE_NUMBER_REGEX = '^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'

    def clean_phone_number(self):
        if self.cleaned_data['phone_number'] is None:
            return
        matcher = re.match(PHONE_NUMBER_REGEX, self.cleaned_data['phone_number'])
        if not matcher:
            raise forms.ValidationError("Invalid number, does not match regex %s" % PHONE_NUMBER_REGEX)
        return self.cleaned_data['phone_number'].replace('(', '').replace(')', '').\
                replace('+', '').replace(' ', '').replace('.', '').replace('-', '').strip()


class TaskForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(choices = DAYS_OF_WEEK)

    class Meta:
        model = Task
        fields = '__all__'

    def clean_month_offset(self):
        month_offset = int(self.cleaned_data['month_offset'])
        if month_offset < 0:
            raise forms.ValidationError("Month offset cannot be a negative integer")
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
