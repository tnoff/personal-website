from django.contrib import admin
from django.urls import path

from homepage.urls import homepage_urls
from my_calendar.urls import my_calendar_urls

urlpatterns = [
    path('9af57e02-325f-4e49-af70-9e83518a8539/', admin.site.urls),
] + my_calendar_urls + homepage_urls
