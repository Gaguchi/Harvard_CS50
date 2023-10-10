
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import User, Post, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-timestamp')
    followers_count = user.followers.count()
    is_following = request.user in user.followers.all()

    context = {
        'profile_user': user,
        'posts': posts,
        'followers_count': followers_count,
        'is_following': is_following,
    }

    return render(request, "network/profile.html", context)


@csrf_exempt
def posts(request):
    if request.method == 'GET':
        # Get the page number from query parameters (default to 1 if not present)
        page_number = request.GET.get('page', 1)

        # Fetch all posts
        all_posts = Post.objects.all().values('id', 'user__id', 'user__username', 'content', 'timestamp').order_by('-timestamp')
        
        # Initialize the paginator
        paginator = Paginator(all_posts, 10)  # Show 10 posts per page

        # Get the Page object for the current page
        current_page = paginator.get_page(page_number)
        
        posts_with_likes = []
        for post in current_page:
            post_id = post['id']
            likes_count = Post.objects.get(id=post_id).likes.count()
            post_with_likes = post.copy()
            post_with_likes['likes_count'] = likes_count
            posts_with_likes.append(post_with_likes)

        return JsonResponse({
            'posts': posts_with_likes,
            'has_next': current_page.has_next(),
            'has_previous': current_page.has_previous(),
            'num_pages': paginator.num_pages
        }, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        content = data.get("content", "")
        post = Post.objects.create(user=user, content=content)
        return JsonResponse({"message": "Post created successfully."}, status=201)
    

@csrf_exempt
@login_required
def comments(request):
    post_id = request.GET.get('post_id', None)
    if request.method == 'GET':
        if post_id:
            comments = Comment.objects.filter(post__id=post_id).values('id', 'user__id', 'user__username', 'post__id', 'content', 'timestamp')
        else:
            comments = Comment.objects.all().values('id', 'user__id', 'post__id', 'content', 'timestamp')
        return JsonResponse(list(comments), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = request.user

        content = data.get("content", "")
        post_id = data.get("post_id", None)

        # Validate content and post_id
        if not content or not post_id:
            return JsonResponse({"error": "Both content and post_id must be provided."}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Invalid post_id."}, status=400)

        comment = Comment.objects.create(user=user, content=content, post=post)
        return JsonResponse({"message": "Comment created successfully."}, status=201)

@csrf_exempt
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment does not exist."}, status=404)
    
    if request.user != comment.user:
        return JsonResponse({"error": "You do not have permission to delete this comment."}, status=403)
    
    comment.delete()
    return JsonResponse({"message": "Comment deleted successfully."})

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
        return JsonResponse({"message": "Post deleted successfully."})
    else:
        return JsonResponse({"error": "You do not have permission to delete this post."}, status=403)

@login_required
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


@csrf_exempt
@login_required  # Require the user to be logged in
def edit_post(request, post_id):
    # Only allow PUT method for editing
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get the post to be edited
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Make sure the logged-in user is the author of the post
    if request.user != post.user:
        return JsonResponse({"error": "Not authorized."}, status=403)

    # Parse the request body for the new content
    data = json.loads(request.body)
    new_content = data.get('content', "")

    # Update the post content
    post.content = new_content
    post.save()

    return JsonResponse({"message": "Post edited successfully."}, status=200)