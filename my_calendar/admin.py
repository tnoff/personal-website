from django.contrib import admin

from my_calendar.forms import BirthdayForm
from my_calendar.models import Birthday, Person

class BirthdayAdmin(admin.ModelAdmin):
    form = BirthdayForm

class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Birthday, BirthdayAdmin)
admin.site.register(Person, PersonAdmin)
