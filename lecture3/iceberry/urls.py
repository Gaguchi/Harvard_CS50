from django.urls import path

from . import views

app_name="iceberry"
urlpatterns = [
    path("", views.index ,name="index"),
]
