from django.contrib import admin

from my_calendar.forms import BirthdayForm, TaskForm
from my_calendar.models import Birthday, Person, Task

class BirthdayAdmin(admin.ModelAdmin):
    form = BirthdayForm

class PersonAdmin(admin.ModelAdmin):
    pass

class TaskAdmin(admin.ModelAdmin):
    form = TaskForm

admin.site.register(Birthday, BirthdayAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Task, TaskAdmin)
