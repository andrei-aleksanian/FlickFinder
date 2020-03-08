from django.shortcuts import render

def home(request):
	return render(request,'main_app/home.html')
def search(request):
	return render(request,'main_app/search.html')
def sign_in(request):
	return render(request,'main_app/sign_in.html')
def sign_up(request):
	return render(request,'main_app/sign_up.html')
def index(request):
	return render(request,'main_app/index.html')
