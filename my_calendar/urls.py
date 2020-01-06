from django.urls import path

from my_calendar import views

my_calendar_urls = [
    path('e37047af-f536-423e-8a72-731cbced13ea/', views.birthdays),
]
