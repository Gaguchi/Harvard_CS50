from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

import random
import re

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(widget=forms.Textarea(attrs={'name': 'body', 'rows': 5}), label="content")

class EditEntryForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(widget=forms.Textarea(attrs={'name': 'body', 'rows': 5}), label="content")

class SearchForm(forms.Form):
    search = forms.CharField(label="search")

def index(request):
    if request.method == 'POST':
        search = SearchForm(request.POST)
        if search.is_valid():
            search_result = search.cleaned_data["search"]
            entry = util.get_entry(search_result)

            if entry:
                return HttpResponseRedirect(reverse('entry', kwargs={'title': search_result}))
            else:
                entries = util.list_entries()
                search_results = [entry for entry in entries if search_result.lower() in entry.lower()]
                return render(request, "encyclopedia/search_results.html", {
                    "search_result": search_result,
                    "entries": search_results
                })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(),
                "search": search
            })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search": SearchForm()
    })

def entry(request, title):
    entry_content = util.get_entry(title)
    if not entry_content:
        return render(request, "encyclopedia/entry_not_found.html", {
            "title": title
        })

    if request.method == 'POST':
        form = EditEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', kwargs={'title': title}))
    else:
        form = EditEntryForm(initial={'title': title, 'content': entry_content})

    html_content = markdown_to_html(entry_content)
    rendered_content = mark_safe(html_content)  # Mark the content as safe HTML

    return render(request, "encyclopedia/entry.html", {
        "entry": rendered_content,  # Use the rendered content in the template
        "title": title,
        "search": SearchForm(),
        "edit_form": form
    })

def new(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm(),
        "search": SearchForm()
    })

def random_entry(request):
    list_entries = util.list_entries()
    random_title = random.choice(list_entries)
    return HttpResponseRedirect(reverse('entry', kwargs={'title': random_title}))

def edit(request):
    title = request.GET.get('title')
    entry_content = util.get_entry(title)
    if not entry_content:
        return render(request, "encyclopedia/entry_not_found.html", {
            "title": title
        })

    if request.method == 'POST':
        form = EditEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', kwargs={'title': title}))
    else:
        form = EditEntryForm(initial={'content': entry_content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "edit_form": form
    })

def markdown_to_html(markdown_content):
    markdown_content = re.sub(r'## (.+?)\n', r'<h2>\1</h2>', markdown_content)
    markdown_content = re.sub(r'# (.+?)\n', r'<h1>\1</h1>', markdown_content)
    markdown_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', markdown_content)
    markdown_content = re.sub(r'\n\* (.+?)\n', r'\n<li>\1</li>', markdown_content)
    markdown_content = re.sub(r'(<li>.+?</li>)', r'<ul>\g<1></ul>', markdown_content)
    markdown_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', markdown_content)
    paragraphs = re.split(r'\n{2,}', markdown_content)
    paragraphs = [f'<p>{p}</p>' for p in paragraphs]
    markdown_content = '\n'.join(paragraphs)

    return markdown_content
