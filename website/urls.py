from django.contrib import admin
from django.urls import path

from homepage import views

urlpatterns = [
    #path('lhnoq7ziwzk3jisw482wd9p50mt2lq58/', admin.site.urls),
    path('', views.home_page),
    path('contact/', views.contact),
]
