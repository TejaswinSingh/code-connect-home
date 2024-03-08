from django.http import HttpResponse
from django.shortcuts import render

def index(request):
	return render(request, "home/index.html")

def register(request):
	return render(request, "home/register.html")
