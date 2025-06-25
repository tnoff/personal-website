from base64 import b64decode
from requests import post
from json import loads
from json.decoder import JSONDecodeError
from django.db import connection
from django.db.utils import OperationalError

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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


def check_authorization(headers):
    if not settings.OCI_WEBHOOK_USER or not settings.OCI_WEBHOOK_PASS:
        return True
    auth_header = headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        return False

    encoded_credentials = auth_header.split(' ')[1]
    decoded = b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded.split(':', 1)

    if username != settings.OCI_WEBHOOK_USER or password != settings.OCI_WEBHOOK_PASS:
        return False
    return True
    

@csrf_exempt
@require_POST
def oci_to_discord(request):
    # Basic Auth validation
    if not check_authorization(request.headers):
        return HttpResponse('Unauthorized', status=401)

    try:
        data = loads(request.body)
    except JSONDecodeError:
        return JsonResponse({"status": "ERROR"})

    # Extract message from OCI format
    message = data.get("message", "No message provided.")

    # Send to Discord
    discord_payload = {"content": message}
    if not settings.DISCORD_WEBHOOK_URL:
        return JsonResponse({"status": "OK"})
    discord_response = post(settings.DISCORD_WEBHOOK_URL, json=discord_payload)

    if discord_response.status_code != 204:
        return JsonResponse({"error": "Failed to send to Discord."}, status=500)

    return JsonResponse({"status": "OK"})