
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    followers = models.ManyToManyField("self", symmetrical=False, related_name='following')

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name="liked_posts")
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=300)
    timestamp = models.DateTimeField(default=timezone.now)
