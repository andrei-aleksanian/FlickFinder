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

#LOAD MOVIE RATINGS IN TO DICTIONARY INDEXED BY MOVIE

# userId - movieId - rating
ratingsFile =  open(os.path.join(workpath, "data/ratings.csv"), "r", encoding="utf-8")
ratingsReader = csv.reader(ratingsFile, delimiter=",")
movieRatings = {}
for rating in ratingsReader:
        if movieRatings.get(rating[1],None) == None:
            movieRatings[rating[1]] = {}
        movieRatings[rating[1]][rating[0]] = float(rating[2])

#REMOVE MOVIES THAT ARE INFREQUENTLY VIEWED

imdbFile =  open(os.path.join(workpath, "data/links.csv"), "r", encoding="utf-8")
imdbReader = csv.reader(imdbFile, delimiter=",")
imdbIds = {}
for imdb in imdbReader:
    imdbIds[imdb[0]] = imdb[1] 
imdbFile.close()    

rm = []
for mov in movieRatings.keys():
    if len(movieRatings[mov]) < 10:
        rm.append(mov)
for mov in rm:
    Movie.objects.get(imdbid=imdbIds[mov]).delete()
    movieRatings.pop(mov)


print(len(movieRatings))


#REMOVE TEST DATA

testing = [{'mov': '300', 'usr': '263', 'r': 3.0}, {'mov': '780', 'usr': '149', 'r': 3.0}, {'mov': '6711', 'usr': '129', 'r': 4.0}, {'mov': '1252', 'usr': '462', 'r': 5.0}, {'mov': '4896', 'usr': '334', 'r': 3.5}, {'mov': '1923', 'usr': '453', 'r': 4.0}, {'mov': '8641', 'usr': '212', 'r': 3.5}, {'mov': '1208', 'usr': '74', 'r': 5.0}, {'mov': '231', 'usr': '68', 'r': 3.5}, {'mov': '70', 'usr': '18', 'r': 3.5}, {'mov': '1080', 'usr': '239', 'r': 4.0}, {'mov': '48780', 'usr': '509', 'r': 3.5}, {'mov': '1356', 'usr': '93', 'r': 5.0}, {'mov': '6942', 'usr': '159', 'r': 4.5}, {'mov': '953', 'usr': '265', 'r': 5.0}, {'mov': '165', 'usr': '588', 'r': 4.0}, {'mov': '736', 'usr': '594', 'r': 4.0}, {'mov': '2987', 'usr': '115', 'r': 5.0}, {'mov': '4878', 'usr': '193', 'r': 4.0}, {'mov': '53125', 'usr': '517', 'r': 2.5}, {'mov': '2502', 'usr': '282', 'r': 4.5}, {'mov': '1617', 'usr': '599', 'r': 3.5}, {'mov': '35836', 'usr': '111', 'r': 3.5}, {'mov': '910', 'usr': '488', 'r': 5.0}, {'mov': '45722', 'usr': '129', 'r': 4.0}, {'mov': '1', 'usr': '477', 'r': 4.0}, {'mov': '141', 'usr': '489', 'r': 3.5}, {'mov': '1356', 'usr': '18', 'r': 4.5}, {'mov': '1645', 'usr': '28', 'r': 2.5}, {'mov': '6874', 'usr': '432', 'r': 2.5}, {'mov': '608', 'usr': '182', 'r': 5.0}, {'mov': '2167', 'usr': '224', 'r': 1.0}, {'mov': '150', 'usr': '477', 'r': 4.0}, {'mov': '1387', 'usr': '483', 'r': 2.0}, {'mov': '80463', 'usr': '298', 'r': 1.5}, {'mov': '6373', 'usr': '331', 'r': 2.0}, {'mov': '4776', 'usr': '239', 'r': 4.0}, {'mov': '2959', 'usr': '593', 'r': 4.0}, {'mov': '1234', 'usr': '431', 'r': 4.0}, {'mov': '370', 'usr': '447', 'r': 4.0}]
for t in testing:
    movieRatings[t["mov"]].pop(t["usr"])
'''
mumFolder =  open(os.path.join(workpath, "data/ppl/mum.txt"),"r",encoding="utf-8")
mumRatings = mumFolder.readlines()
for i in mumRatings:
    i = i.rstrip("\n").split()
    movieRatings[i[0]]["mum"] = float(i[1])
mumFolder.close()
'''
sampFolder =  open(os.path.join(workpath, "data/ppl/samp.txt"),"r",encoding="utf-8")
sampRatings = sampFolder.readlines()
for i in sampRatings:
    i = i.rstrip("\n").split()
    movieRatings[i[0]]["samp"] = float(i[1])
sampFolder.close()

#REINDEX RATING DATA BY USERS

userRatings = {}
for mov in movieRatings:
    for usr in movieRatings[mov]:
        if userRatings.get(usr,None) == None:
            userRatings[usr] = {}
        userRatings[usr][mov] = movieRatings[mov][usr]


#LOAD MOVIE TITLE DATA

# movieId - title
moviesFile =  open(os.path.join(workpath, "data/movies.csv"), "r", encoding="utf-8")
moviesReader = csv.reader(moviesFile, delimiter=",")
movieNames = {}
movieIDs = {}
for movie in moviesReader:
    movieNames[movie[0]] = movie[1]
    movieIDs[movie[1]] = movie[0]


#for mov in movieRatings:
#    print(mov + " - " + movieNames[mov] + " has been seen " + str(len(movieRatings[mov])) + " times.")


#GENERATE MATRIX FACTORS
global P,Q
K = 70
# [movieID][k]
P = {}
for movie in movieRatings:
    P[movie] = [ x * math.sqrt(5/K) for x in numpy.random.rand(K).tolist()]
# [userID][k]
Q = {}
for user in userRatings:
    Q[user] = [x * math.sqrt(5/K) for x in numpy.random.rand(K).tolist()]

#LOAD IN SAVED FACTOR DATA
'''
fileP =  open(os.path.join(workpath, "p.obj"),"rb")
fileQ =  open(os.path.join(workpath, "q.obj"),"rb")
savedP = pickle.load(fileP)
savedQ = pickle.load(fileQ)
for p in savedP:
    for p1 in range(len(savedP[p])):
        P[p][p1] = savedP[p][p1]
for q in savedQ:
    for q1 in range(len(savedQ[q])):
        Q[q][q1] = savedQ[q][q1]
fileP.close()
fileQ.close()
print("FILE LOADED")
'''

def matfact(alpha = 0.0002, beta = 0.002):
    tnow = time.time()
    global P,Q
    for x in movieRatings:
        #x = movieId
        try:    
            for y in movieRatings[x]:
                #y = userId
                eij = movieRatings[x][y] - numpy.dot(P[x],Q[y])
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

def test():
    tot = 0
    for t in testing:
        print("")
        print(t["mov"] + " - " + movieNames[t["mov"]] + " was rated " + str(t["r"]) + " by user " + t["usr"])
        print("User " + t["usr"] + " has seen " + str(len(userRatings[t["usr"]])) + " films in this database")
        print("Film " + t["mov"] + " has " + str(len(movieRatings[t["mov"]])) + " views in this database")
        prediction = numpy.dot(P[t["mov"]],Q[t["usr"]])
        print("Our prediction is : " + str(prediction))
        print(movieRatings[t["mov"]].get(t["usr"],None))
        print(userRatings[t["usr"]].get(t["mov"],None))
        print("")
        tot += abs(t["r"] - prediction)**2
    tot = math.sqrt(tot)
    tot /= len(testing)
    print("Mean error = " + str(tot))
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

    recommend = []
    for film in P:
        if film not in userRatings[uid]:
            urate = numpy.dot(P[film], Q[uid])
            obj = [urate, movieNames[film], film]
            i = 0
            try:
                while recommend[i][0] > urate:
                    i += 1
                recommend.insert(i, obj)
            except IndexError:
                recommend.append(obj)

    return HttpResponse(recommend[offset*40:(offset+1)*40])

def viewed(request, uid):
    if uid not in Q:
        return HttpResponse("This user doesnt exist")
    viewed = []
    for movie in userRatings[uid]:
        obj = [userRatings[uid][movie], movieNames[movie], movie]
        i = 0
        try:
            while viewed[i][0] > userRatings[uid][movie]:
                i+=1
            viewed.insert(i, obj)
        except IndexError:
             viewed.append(obj)

    return HttpResponse(viewed)


def deluser(request, uid):
    try:    
        del Q[uid]
        del userRatings[uid]
        for i in movieRatings:
            if uid in movieRatings[i]:
                del movieRatings[i][uid]
        saveData()
        return HttpResponse("User deleted")
    except:
        return HttpResponse("This user doesnt exist")


def update():
    while True:
        matfact(alpha=0.004)

#if "runserver" in sys.argv:
#    threading.Thread(target = update).start()

imdbFile =  open(os.path.join(workpath, "data/links.csv"), "r", encoding="utf-8")
imdbReader = csv.reader(imdbFile, delimiter=",")
imdbIds = {}
for imdb in imdbReader:
    imdbIds[imdb[0]] = imdb[1] 
imdbFile.close()    

def moviesCSV(request):
    output = ""
    for id in movieNames:
        output += "\"" + imdbIds[id] + "\",\"" + movieNames[id] + "\"\n"
    return HttpResponse(output)

def ratingsCSV(request):
    output = ""
    for movieId in movieRatings:
        for userId in movieRatings[movieId]:
            output += "\"" + imdbIds[movieId] + "\",\"" + userId + "\"," + str(movieRatings[movieId][userId]) + "\n" 
    return HttpResponse(output)

urlpatterns = [
    path('home/', views.home),
    path('search/', views.search),
    path('login/', views.sign_in),
    path('register/', views.sign_up),
    path('', views.index),
    path('api/recommend/<uid>/<int:offset>/', recommender),
    path('api/viewed/<uid>/', viewed),
    path('del/<uid>/', deluser),
    path('movies/', moviesCSV),
    path('ratings/', ratingsCSV)
]
