from django import forms

from basketball.models import Game, Team

from my_calendar.models import Person, Task


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def clean_year(self):
        year = int(self.cleaned_data['year'])
        if year < 1900 or year > 2100:
            raise forms.ValidationError(f'Invalid year given {year}')
        return year

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'

    def clean_away_score(self):
        score = int(self.cleaned_data['away_score'])
        if score < 0 or score > 200:
            raise forms.ValidationError(f'Invalid score given {score}')
        return score

    def clean_home_score(self):
        score = int(self.cleaned_data['home_score'])
        if score < 0 or score > 200:
            raise forms.ValidationError(f'Invalid score given {score}')
        return score

