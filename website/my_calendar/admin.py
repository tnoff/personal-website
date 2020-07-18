from django.contrib import admin

from my_calendar.forms import PersonForm, TaskForm
from my_calendar.models import Group, Person, Task, WebsiteUserSettings

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm

class TaskAdmin(admin.ModelAdmin):
    form = TaskForm

class GroupAdmin(admin.ModelAdmin):
    pass

class WebsiteUserSettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Person, PersonAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(WebsiteUserSettings, WebsiteUserSettingsAdmin)
