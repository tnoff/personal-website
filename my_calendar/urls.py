from django.urls import path, re_path

from my_calendar import views

my_calendar_urls = [
    path('e37047af-f536-423e-8a72-731cbced13ea/', views.birthdays),
    path('0d27c6b9-a5d7-4782-9438-93b54b8f98f8/', views.tasks),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/done', views.task_mark_done),
]
