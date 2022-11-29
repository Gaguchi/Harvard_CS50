from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(label="content")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "entry" : util.get_entry(title),
        "title": title
    })

def new(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            f = open(f'./entries/{title}.md', "w")
            f.write(f'{content}')
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "encyclopedia/new.html",{
                "form":form
            })
    return render(request, "encyclopedia/new.html",{
        "form":NewEntryForm()
    })