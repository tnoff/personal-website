from django.shortcuts import render

def home_page(request):
    return render(request, 'homepage/index.html')

def contact(request):
    return render(request, 'homepage/contact.html')

def resume(request):
    return render(request, 'homepage/resume.html')

def projects(request):
    return render(request, 'homepage/projects.html')
