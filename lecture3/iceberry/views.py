from django.shortcuts import render

from .models import Ice_Cream
# Create your views here.

def index(request):
    # return HttpResponse("Hello, world!")
    return render(request, "iceberry/index.html", {
        "products": Ice_Cream.objects.all()
    })
