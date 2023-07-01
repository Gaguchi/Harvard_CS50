from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchers')

    def add_to_watchlist(self, listing):
        self.watchlist.add(listing)

    def remove_from_watchlist(self, listing):
        self.watchlist.remove(listing)

    def clear_watchlist(self):
        self.watchlist.clear()


class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.current_price or self.current_price < self.starting_bid:
            self.current_price = self.starting_bid
        super().save(*args, **kwargs)

    def has_highest_bid(self, user):
        highest_bid = self.highest_bid()
        return highest_bid and highest_bid.bidder == user

    def highest_bid(self):
        return self.bids.order_by('-amount').first()

    @property
    def is_closed(self):
        return not self.active

    def is_listing_creator(self, user):
        return user == self.creator


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.listing.current_price = self.amount
        self.listing.save()


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter.username} - {self.content[:50]}"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
