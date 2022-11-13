from django.shortcuts import render
from django.http import HttpResponse
import datetime
# Create your views here.

#HERE IS MY VERSION

# def index(request):
#     now = datetime.datetime.now()

#     def is_it_ny(now):
#         if now.month == 1 and now.day == 1:
#             True
#         else:
#             False

#     if is_it_ny == True:
#         return HttpResponse("It's New Years!")
#     else:
#         return HttpResponse("It's not New Years!")

#HERE IS THE LECTURE VERSION

def index(request):
    now = datetime.datetime.now()
    return render(request, "newyear/index.html",{
        "newyear": now.month == 1 and now.day ==1
    })