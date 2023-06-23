from django.shortcuts import render

# Create your views here.
def index(response):
    return render(response , template_name="app/index.html")