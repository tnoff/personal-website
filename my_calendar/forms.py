from django import forms

from my_calendar.constants import DAYS_OF_WEEK, MONTHS
from my_calendar.models import Task

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
