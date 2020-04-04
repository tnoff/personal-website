from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import render

def home_page(request):
    return render(request, 'homepage/index.html')

def contact(request):
    return render(request, 'homepage/contact.html')

def resume(request):
    return render(request, 'homepage/resume.html')

def projects(request):
    return render(request, 'homepage/projects.html')

def health_check(request):
    try:
        connection.ensure_connection()
        return HttpResponse('OK', status=200)
    except OperationalError:
        return HttpResponse('FAIL', status=500)
