from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from . import views
import csv
import math
import numpy
import time
import threading
import random
import pickle
import os
import sys
from main_app.models import Movie
from main_app.models import User
from main_app.models import Rating

workpath = os.path.dirname(os.path.abspath(__file__))

#ISOLATED TEST DATA
testing = [{'mov': '300', 'usr': '263', 'r': 3.0}, {'mov': '780', 'usr': '149', 'r': 3.0}, {'mov': '6711', 'usr': '129', 'r': 4.0}, {'mov': '1252', 'usr': '462', 'r': 5.0}, {'mov': '4896', 'usr': '334', 'r': 3.5}, {'mov': '1923', 'usr': '453', 'r': 4.0}, {'mov': '8641', 'usr': '212', 'r': 3.5}, {'mov': '1208', 'usr': '74', 'r': 5.0}, {'mov': '231', 'usr': '68', 'r': 3.5}, {'mov': '70', 'usr': '18', 'r': 3.5}, {'mov': '1080', 'usr': '239', 'r': 4.0}, {'mov': '48780', 'usr': '509', 'r': 3.5}, {'mov': '1356', 'usr': '93', 'r': 5.0}, {'mov': '6942', 'usr': '159', 'r': 4.5}, {'mov': '953', 'usr': '265', 'r': 5.0}, {'mov': '165', 'usr': '588', 'r': 4.0}, {'mov': '736', 'usr': '594', 'r': 4.0}, {'mov': '2987', 'usr': '115', 'r': 5.0}, {'mov': '4878', 'usr': '193', 'r': 4.0}, {'mov': '53125', 'usr': '517', 'r': 2.5}, {'mov': '2502', 'usr': '282', 'r': 4.5}, {'mov': '1617', 'usr': '599', 'r': 3.5}, {'mov': '35836', 'usr': '111', 'r': 3.5}, {'mov': '910', 'usr': '488', 'r': 5.0}, {'mov': '45722', 'usr': '129', 'r': 4.0}, {'mov': '1', 'usr': '477', 'r': 4.0}, {'mov': '141', 'usr': '489', 'r': 3.5}, {'mov': '1356', 'usr': '18', 'r': 4.5}, {'mov': '1645', 'usr': '28', 'r': 2.5}, {'mov': '6874', 'usr': '432', 'r': 2.5}, {'mov': '608', 'usr': '182', 'r': 5.0}, {'mov': '2167', 'usr': '224', 'r': 1.0}, {'mov': '150', 'usr': '477', 'r': 4.0}, {'mov': '1387', 'usr': '483', 'r': 2.0}, {'mov': '80463', 'usr': '298', 'r': 1.5}, {'mov': '6373', 'usr': '331', 'r': 2.0}, {'mov': '4776', 'usr': '239', 'r': 4.0}, {'mov': '2959', 'usr': '593', 'r': 4.0}, {'mov': '1234', 'usr': '431', 'r': 4.0}, {'mov': '370', 'usr': '447', 'r': 4.0}]

#GENERATE MATRIX FACTORS
global P,Q
K = 70
# [movieID][k]
P = {}
for movie in Movie.objects.all():
    P[movie.imdbid] = [ x * math.sqrt(5/K) for x in numpy.random.rand(K).tolist()]
# [userID][k]
Q = {}
for user in User.objects.all():
    Q[user.username] = [x * math.sqrt(5/K) for x in numpy.random.rand(K).tolist()]

#LOAD IN SAVED FACTOR DATA
fileP =  open(os.path.join(workpath, "p.obj"),"rb")
fileQ =  open(os.path.join(workpath, "q.obj"),"rb")
'''
savedP = pickle.load(fileP)
savedQ = pickle.load(fileQ)
for p in savedP:
    for p1 in range(len(savedP[p])):
        P[p][p1] = savedP[p][p1]
for q in savedQ:
    for q1 in range(len(savedQ[q])):
        Q[q][q1] = savedQ[q][q1]
'''
fileP.close()
fileQ.close()
print("MATRICES LOADED")


def matfact(alpha = 0.0002, beta = 0.002):
    tnow = time.time()
    global P,Q
    for rating in Rating.objects.all():
        try:    
            #x = movieId
            x = rating.movie_id
            #y = userId
            y = rating.user_id
            eij = rating.rating - numpy.dot(P[x],Q[y])
            for k in range(K):
                Q[y][k] += alpha * (2 * eij * P[x][k] - beta * Q[y][k])
                P[x][k] += alpha * (2 * eij * Q[y][k] - beta * P[x][k])
                if abs(P[x][k]) > 100:
                    print("A big number was stored: P[" + x + "," + str(k) + "] = " + str(abs(P[x][k])))
                    print(eij)
                if abs(Q[y][k]) > 100:
                    print("A big number was stored: Q[" + y + "," + str(k) + "] = " + str(abs(Q[y][k])))
                    print(eij)
        except:
            print("User deleted affected SVC.")
    print(time.time()-tnow)
    print("------------------------------")


def saveData():
    global P,Q
    fileP =  open(os.path.join(workpath, "p.obj"), "wb")
    fileQ =  open(os.path.join(workpath, "q.obj"), "wb")
    pickle.dump(P, fileP)
    pickle.dump(Q, fileQ)
    fileP.close()
    fileQ.close()
    print("WROTE TO FILE")


def recommender(request, uid, offset):
    if uid not in Q:
        return HttpResponse("This user doesnt exist")
    query = Rating.objects.filter(user_id=uid)
    seenFilms = []
    for q in query:
        seenFilms.append(q.movie_id)   
    recommend = []
    for film in P:
        if film not in seenFilms:
            urate = numpy.dot(P[film], Q[uid])
            recommend.append([urate, film])
    recommend = mergesort(recommend)
    response = "["
    for i in range(offset*40, (offset+1)*40):
        response += '{"rating":' + str(recommend[i][0]) + ', "id":"' + str(recommend[i][1]) + '", "title":"' + Movie.objects.get(imdbid=recommend[i][1]).title + '"},' 
    response = response[:-1]
    response += "]"
    return HttpResponse(response)


def mergesort(array):
    if len(array) < 2:
        return array
    else:
        mid = int(len(array)/2)
        a1 = mergesort(array[0:mid])
        a2 = mergesort(array[mid:len(array)])
        output = []
        while(len(a1)!=0 and len(a2)!=0):
            if a1[0][0] > a2[0][0]:
                output.append(a1.pop(0))
            else:
                output.append(a2.pop(0))
        while(len(a1)!=0):
            output.append(a1.pop(0))
        while(len(a2)!=0):
            output.append(a2.pop(0))
        return output


def viewed(request, uid):
    if uid not in Q:
        return HttpResponse("This user doesnt exist")
    query = Rating.objects.filter(user_id=uid).order_by("-rating")
    viewed = "["
    for q in query:
        viewed += '{"rating":' + str(q.rating) + ', "id":"' + q.movie_id + '", "title":"' + Movie.objects.get(imdbid=q.movie_id).title + '"},'
    viewed = viewed[:-1]
    viewed += "]"
    return HttpResponse(viewed)


def deluser(request, uid):
    try:    
        del Q[uid]
        saveData()
        User.objects.get(username=uid).delete()
        return HttpResponse("User deleted")
    except:
        return HttpResponse("This user doesnt exist")


def update():
    while True:
        matfact(alpha=0.004)

if "runserver" in sys.argv:
    threading.Thread(target = update).start()


urlpatterns = [
    path('', views.log),
    path('home/', views.home),
    path('condition/', views.condition),
    path('register/', views.register),
    path('Aboutus/', views.aboutus),
    path('privacy/', views.privacy),
    path('rating/', views.rating),
    path('api/recommend/<uid>/<int:offset>/', recommender),
    path('api/viewed/<uid>/', viewed),
    path('del/<uid>/', deluser),
]