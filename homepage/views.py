import logging

from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import render


logger = logging.getLogger(__name__)

def home_page(request):
    '''
    Show homepage
    '''
    return render(request, 'homepage/index.html')

def contact(request):
    '''
    Show contact page
    '''
    return render(request, 'homepage/contact.html')

def resume(request):
    '''
    Show resume page
    '''
    return render(request, 'homepage/resume.html')

def projects(request):
    '''
    Show projects page
    '''
    return render(request, 'homepage/projects.html')

def health_check(_request):
    '''
    Check connection to database
    '''
    try:
        connection.ensure_connection()
        return HttpResponse('OK', status=200)
    except OperationalError:
        return HttpResponse('FAIL', status=500)