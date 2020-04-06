from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

def home(request):
	return render(request,'main_app/home.html')
def aboutus(request):
	return render(request,'main_app/Aboutus.html')
def register(request):
	return render(request,'main_app/register.html')
def condition(request):
	return render(request,'main_app/condition.html')
def log(request):
	return render(request,'main_app/log.html')
def privacy(request):
	return render(request,'main_app/privacy.html')
def rating(request):
	return render(request,'main_app/rating.html')
def index(request):
	return render(request,'main_app/index.html')
