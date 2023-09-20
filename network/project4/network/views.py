
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import User, Post, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

def index(request):
    return render(request, "network/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]


@csrf_exempt
@login_required
def posts(request):
    if request.method == 'GET':
        posts = list(Post.objects.values())
        return JsonResponse(posts, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        content = data.get("content", "")
        post = Post.objects.create(user=user, content=content)
        return JsonResponse({"message": "Post created successfully."}, status=201)

def followed_posts(request):
    user = request.user
    followed_users = user.following.all()
    posts = Post.objects.filter(user__in=followed_users).values()
    return JsonResponse(list(posts), safe=False)

def liked_posts(request):
    user = request.user
    posts = Post.objects.filter(likes=user).values()
    return JsonResponse(list(posts), safe=False)
