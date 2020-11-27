from django.urls import path, re_path

from my_calendar import views

my_calendar_urls = [
    path('e37047af-f536-423e-8a72-731cbced13ea/', views.persons),
    path('0d27c6b9-a5d7-4782-9438-93b54b8f98f8/', views.task_list),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/create', views.task_create),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/?$', views.task_show),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/done', views.task_mark_done),
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/?$', views.calendar),
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/(?P<year>\d+)/?$', views.calendar),
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/(?P<year>\d+)/(?P<month>\d+)/$', views.calendar),
    re_path(r'6a8a3ce2-a91f-4605-8010-145c113d467f/(?P<event_id>\d+)/?$', views.event_show),
]
