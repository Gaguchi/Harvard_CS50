
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.posts, name="posts"),
    path("comments", views.comments, name="comments"),
    path("followed_posts", views.followed_posts, name="followed_posts"),
    path("liked_posts", views.liked_posts, name="liked_posts"),
    path('like_post/<int:post_id>', views.like_post, name='like_post'),
    path('follow_user/<int:user_id>', views.follow_user, name='follow_user'),
    path('delete_post/<int:post_id>', views.delete_post, name='delete_post'),
    path('delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),
    path('get_username', views.get_username, name='get_username'),
    path("profile/<str:username>", views.profile, name="profile"),
]
