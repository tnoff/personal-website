from django.urls import path

from homepage import views

homepage_urls = [
    path('', views.home_page),
    path('contact/', views.contact),
    path('resume/', views.resume),
    path('projects/', views.projects),
]
