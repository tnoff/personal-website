from django.shortcuts import render

def home_page(request):
    return render(request, 'homepage/index.html')

def contact(request):
    return render(request, 'homepage/contact.html')
