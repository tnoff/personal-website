from django.contrib import admin

from my_calendar.forms import TaskForm
from my_calendar.models import Person, Task

class PersonAdmin(admin.ModelAdmin):
    pass

class TaskAdmin(admin.ModelAdmin):
    form = TaskForm

admin.site.register(Person, PersonAdmin)
admin.site.register(Task, TaskAdmin)
