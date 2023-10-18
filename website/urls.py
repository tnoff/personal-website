from django.contrib import admin
from django.urls import include, path


from homepage.urls import homepage_urls


urlpatterns = [
] + homepage_urls
