from django.urls import path, re_path

from my_calendar import views

my_calendar_urls = [
    # Person urls
    re_path(r'e37047af-f536-423e-8a72-731cbced13ea/?$', views.people_list),
    re_path(r'e37047af-f536-423e-8a72-731cbced13ea/create/?$', views.person_create),
    re_path(r'e37047af-f536-423e-8a72-731cbced13ea/(?P<person_id>\d+)/?$', views.person_update),
    re_path(r'e37047af-f536-423e-8a72-731cbced13ea/(?P<person_id>\d+)/delete/?$', views.person_delete),
    # Group urls
    re_path(r'c7063309-ff0a-4e95-8157-2d07bf6d3ea3/create/$', views.group_create),
    # Task urls
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/?$', views.task_list),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/create/?$', views.task_create),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/?$', views.task_show),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/edit/?$', views.task_update),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/delete/?$', views.task_delete),
    re_path(r'0d27c6b9-a5d7-4782-9438-93b54b8f98f8/(?P<task_id>\d+)/done/?$', views.task_mark_done),
    # Event urls
    re_path(r'6a8a3ce2-a91f-4605-8010-145c113d467f/(?P<event_id>\d+)/?$', views.event_show),
    # Calendar urls
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/?$', views.calendar),
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/(?P<year>\d+)/?$', views.calendar),
    re_path(r'5065f9f1-fca3-4a6c-ba4c-e8cb13b0d95e/(?P<year>\d+)/(?P<month>\d+)/?$', views.calendar),
]
