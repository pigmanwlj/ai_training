from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import appvpn
from myapp.models import appjump

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the myapp index.")

def add(request):
    lists = appvpn.objects.all()
    for appvpn in lists:
        print(appvpn)

    print(appvpn.objects.get(id=3))
    return HttpResponse("Add......")

def add(request):
    lists = appjump.objects.all()
    for appjump in lists:
        print(appjump)

    print(appjump.objects.get(id=3))
    return HttpResponse("Add......")

