import re
import string

from django import forms

from my_calendar.constants import DAYS_OF_WEEK
from my_calendar.models import Event, Group, Person, Task

# https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
PHONE_NUMBER_REGEX = r'^(\+?\d{1,2})?(\s)?\(?\d{3}\)?([\s.-])?\d{3}([\s.-])?\d{4}'


class PersonForm(forms.ModelForm):
    '''
    Form for Person model
    '''
    class Meta:
        '''
        Needed for form
        '''
        model = Person
        fields = '__all__'

    def clean_phone_number(self):
        '''
        Make sure phone number matches docstring
        '''
        if self.cleaned_data['phone_number'] is None:
            return None
        matcher = re.match(PHONE_NUMBER_REGEX, self.cleaned_data['phone_number'])
        if not matcher:
            raise forms.ValidationError('Invalid number, '\
                                        f'does not match regex {PHONE_NUMBER_REGEX}')
        just_digits = ''.join(digit for digit in self.cleaned_data['phone_number'] \
                                if digit in string.digits)
        # If only 10 digits given, assume its a use code
        if len(just_digits) == 10:
            return f'+1{just_digits}'
        return f'+{just_digits}'

class GroupForm(forms.ModelForm):
    '''
    Form for group model
    '''
    class Meta:
        '''
        Needed for form
        '''
        model = Group
        fields = '__all__'

class EventForm(forms.ModelForm):
    '''
    Form for event model
    '''
    class Meta:
        '''
        Needed for form
        '''
        model = Event
        fields = '__all__'

    def clean_end(self):
        '''
        Ensure start and end time are valid
        '''
        if self.cleaned_data['start'] > self.cleaned_data['end']:
            raise forms.ValidationError('Start of event must come before end')
        if self.cleaned_data['end'].day != self.cleaned_data['start'].day:
            raise forms.ValidationError('Events cannot span multiple days')
        return self.cleaned_data['end']

class TaskForm(forms.ModelForm):
    '''
    Form for Task Event
    '''
    day_of_week = forms.ChoiceField(choices = DAYS_OF_WEEK)

    class Meta:
        '''
        Needed for form
        '''
        model = Task
        fields = '__all__'

    def clean_month_offset(self):
        '''
        Ensure month offset within proper range
        '''
        month_offset = int(self.cleaned_data['month_offset'])
        if month_offset < 0:
            raise forms.ValidationError("Month offset cannot be a negative integer")
        if month_offset > 6:
            raise forms.ValidationError("Month offset cannot be greater than 6")
        return month_offset

    def clean_week_offset(self):
        '''
        Ensure week offset within proper range
        '''
        week_offset = int(self.cleaned_data['week_offset'])
        if week_offset < 1:
            raise forms.ValidationError("Week offset must be positive integer")
        if week_offset > 4:
            raise forms.ValidationError("Week offset cannot be greater than 4")
        return week_offset
