from requests import post
from json import loads, dumps
from json.decoder import JSONDecodeError
import logging

from django.db import connection
from django.db.utils import OperationalError
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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
    
@csrf_exempt
@require_POST
def oci_to_discord(request):
    try:
        data = loads(request.body)
    except JSONDecodeError:
        return JsonResponse({"status": "ERROR"})


    # Send to Discord
    discord_payload = {"content": f'```{dumps(data, indent=2)}```'}
    if not settings.DISCORD_WEBHOOK_URL:
        return JsonResponse({"status": "OK"})
    discord_response = post(settings.DISCORD_WEBHOOK_URL, json=discord_payload)

    if discord_response.status_code != 204:
        return JsonResponse({"error": "Failed to send to Discord."}, status=500)

    return JsonResponse({"status": "OK"})