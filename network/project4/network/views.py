
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
def posts(request):
    if request.method == 'GET':
        posts = Post.objects.all().values('id', 'user__id', 'user__username', 'content', 'timestamp')
        return JsonResponse(list(posts), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        content = data.get("content", "")
        post = Post.objects.create(user=user, content=content)
        return JsonResponse({"message": "Post created successfully."}, status=201)

@csrf_exempt
@login_required
def like_post(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return JsonResponse({"message": "Liked successfully."}, status=201)


def followed_posts(request):
    user = request.user
    posts = Post.objects.filter(user__followers=user).values('id', 'user__id', 'user__username', 'content', 'timestamp')
    return JsonResponse(list(posts), safe=False)

def liked_posts(request):
    user = request.user
    posts = Post.objects.filter(likes=user).values('id', 'user__id', 'user__username', 'content', 'timestamp')
    return JsonResponse(list(posts), safe=False)

def get_username(request):
    if request.user.is_authenticated:
        return JsonResponse({"username": request.user.username})
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)

@csrf_exempt
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.user:
        post.delete()
        return JsonResponse({"message": "Post deleted successfully."}, status=204)
    else:
        return JsonResponse({"error": "You do not have permission to delete this post."}, status=403)

@csrf_exempt
def follow_user(request, user_id):
    # Get the user to be followed or unfollowed
    user_to_follow = User.objects.get(id=user_id)

    # Get the current user
    current_user = request.user

    # Check if the current user already follows the user to be followed
    if user_to_follow.followers.filter(id=current_user.id).exists():
        # Unfollow
        user_to_follow.followers.remove(current_user)
        return JsonResponse({"message": "Unfollowed successfully."})
    else:
        # Follow
        user_to_follow.followers.add(current_user)
        return JsonResponse({"message": "Followed successfully."})

