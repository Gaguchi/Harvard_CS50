from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import random

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(label="content")

class SearchForm(forms.Form):
    search = forms.CharField(label="search")

def index(request):
    if request.method == 'POST':
        search = SearchForm(request.POST)
        if search.is_valid():
            search_result = search.cleaned_data["search"]
            return HttpResponseRedirect(f'/{search_result}')
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(),
                "search": search
            })
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search":SearchForm()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "entry" : util.get_entry(title),
        "title": title,
        "search":SearchForm()
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
        "form":NewEntryForm(),
        "search":SearchForm()
    })

def random_entry(request):
    list = util.list_entries()
    return HttpResponseRedirect(random.choice(list))
