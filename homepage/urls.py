from django.urls import path

from homepage import views

homepage_urls = [
    path('', views.home_page),
    path('resume/', views.resume),
    path('projects/', views.projects),
    path('_health/', views.health_check),
    path('e1ac9a48-3a69-4ef8-9033-ec38f83dd9dc/', views.oci_to_discord, name='oci_to_discord')
]
