from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .forms import CommentForm
from .models import Listing, Bid, Comment, Category

from .models import User
from .forms import CreateListingForm


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreateListingForm()
    
    return render(request, 'auctions/create_listing.html', {'form': form})


def index(request):
    active_listings = Listing.objects.filter(active=True)
    is_authenticated = request.user.is_authenticated
    watchlist = request.user.watchlist.all() if is_authenticated else []
    active_listings_with_data = []
    for listing in active_listings:
        is_watchlisted = watchlist.filter(pk=listing.id).exists() if is_authenticated else False
        has_highest_bid = listing.has_highest_bid(request.user) if is_authenticated else False
        is_listing_creator = listing.creator == request.user if is_authenticated else False
        is_closed = not listing.active
        active_listings_with_data.append({
            'listing': listing,
            'listing_id': listing.id,
            'is_watchlisted': is_watchlisted,
            'has_highest_bid': has_highest_bid,
            'is_listing_creator': is_listing_creator,
            'is_closed': is_closed
        })

    context = {
        'active_listings': active_listings_with_data,
        'is_authenticated': is_authenticated,
    }
    return render(request, 'auctions/index.html', context)


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    is_authenticated = request.user.is_authenticated

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.commenter = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = CommentForm()

    context = {
        'listing': listing,
        'is_authenticated': is_authenticated,
        'form': form,  # Include the CommentForm in the context
    }
    return render(request, 'auctions/listing_detail.html', context)


def categories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'auctions/categories.html', context)


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    active_listings = category.listing_set.filter(active=True)
    context = {
        'category': category,
        'active_listings': active_listings
    }
    return render(request, 'auctions/category_listings.html', context)


@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.commenter = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = CommentForm()

    context = {
        'form': form,
        'listing': listing,
    }

    return render(request, 'auctions/add_comment.html', context)


@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist = request.user.watchlist

    if listing not in watchlist.all():
        watchlist.add(listing)
        messages.success(request, 'Listing added to your watchlist.')
    else:
        messages.error(request, 'Listing is already in your watchlist.')

    return redirect('index')

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        request.user.watchlist.remove(listing)
        messages.success(request, 'Listing removed from your watchlist.')
    return redirect('index')

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        amount = Decimal(request.POST['bid_amount'])
        if amount >= listing.starting_bid and (not listing.bids.exists() or amount > listing.current_price):
            Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
            messages.success(request, 'Bid placed successfully.')
        else:
            messages.error(request, 'Invalid bid amount.')
    return redirect('index')


@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        highest_bid = listing.highest_bid()
        if highest_bid:
            listing.active = False
            listing.save()
            messages.success(request, f'Auction closed. {highest_bid.bidder.username} has won the auction.')
        else:
            messages.error(request, 'No bids placed on this listing.')
    return redirect('index')
