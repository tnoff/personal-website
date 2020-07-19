from django.contrib import admin

from my_calendar.forms import EventForm, PersonForm, TaskForm
from my_calendar.models import Event, Group, Person, Task, WebsiteUserSettings

class EventAdmin(admin.ModelAdmin):
    form = EventForm

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm

class TaskAdmin(admin.ModelAdmin):
    form = TaskForm

class GroupAdmin(admin.ModelAdmin):
    pass

class WebsiteUserSettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(WebsiteUserSettings, WebsiteUserSettingsAdmin)
