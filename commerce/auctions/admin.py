from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'current_price', 'creator', 'created_at', 'active']
    list_filter = ['active', 'category', 'creator']
    search_fields = ['title', 'description']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing', 'bidder', 'amount', 'created_at']
    list_filter = ['listing', 'bidder']
    search_fields = ['listing__title', 'bidder__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'commenter', 'content', 'created_at']
    list_filter = ['listing', 'commenter']
    search_fields = ['listing__title', 'commenter__username']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
