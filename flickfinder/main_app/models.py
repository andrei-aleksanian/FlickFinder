from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    password = models.CharField(max_length=256)

class Movie(models.Model):
    imdbid = models.CharField(max_length=7, primary_key=True)
    title = models.CharField(max_length=256)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()