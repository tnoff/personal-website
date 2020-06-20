from django.contrib import admin
from django.urls import include, path

from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired

from basketball.urls import basketball_urls
from homepage.urls import homepage_urls
from my_calendar.urls import my_calendar_urls

admin.site.__class__ = AdminSiteOTPRequired

urlpatterns = [
    path('', include(tf_urls)),
    path('9af57e02-325f-4e49-af70-9e83518a8539/', admin.site.urls),
] + my_calendar_urls + homepage_urls + basketball_urls
