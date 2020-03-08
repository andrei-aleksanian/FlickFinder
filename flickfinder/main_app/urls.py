from django.urls import path
from . import views
urlpatterns = [
    path('home/', views.home),
    path('search/', views.search),
    path('login/', views.sign_in),
    path('register/', views.sign_up),
    path('', views.index),

]
