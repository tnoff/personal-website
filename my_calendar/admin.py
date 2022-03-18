from django.contrib import admin

from my_calendar.forms import EventForm, PersonForm, TaskForm
from my_calendar.models import Event, Group, Person, Task, UserSettings

class EventAdmin(admin.ModelAdmin):
    '''
    Admin for Event Model
    '''
    form = EventForm

class PersonAdmin(admin.ModelAdmin):
    '''
    Admin for Person Model
    '''
    form = PersonForm

class TaskAdmin(admin.ModelAdmin):
    '''
    Admin for Task Model
    '''
    form = TaskForm

class GroupAdmin(admin.ModelAdmin):
    '''
    Admin for Group Model
    '''

class UserSettingsAdmin(admin.ModelAdmin):
    '''
    Admin for Website Settings Model
    '''

admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
