from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Listings, Bids, Comments, Category
from .forms import ListingForm
from django.contrib import messages

from .models import User


def index(request):
    active_listings = Listings.objects.filter(is_active=True)

    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


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


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("index")
    else:
        form = ListingForm()

    return render(request, "auctions/create.html", {
        "form": form
    })


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    highest_bid = Bids.objects.filter(
        listing=listing).order_by('bid_amount').first()
    current_bid = highest_bid.bid_amount if highest_bid else listing.starting_bid

    if request.method == "POST" and 'add_watchlist' in request.POST:
        if request.user in listing.watchlist.all():
            listing.watchlist.remove(request.user)
            messages.success(request, "Removed from your watchlist.")
        else:
            listing.watchlist.add(request.user)
            messages.success(request, "Added to your watchlist.")
        return redirect('listing_detail', listing_id=listing.id)

    if request.method == "POST" and 'place_bid' in request.POST:
        bid_amount = request.POST.get("bid_amount")
        if not bid_amount:
            messages.error(request, "Please enter a bid amount.")
            return redirect('listing_detail', listing_id=listing.id)

        try:
            bid_amount = float(bid_amount)
        except ValueError:
            messages.error(request, "Invalid bid amount.")
            return redirect('listing_detail', listing_id=listing.id)

        if bid_amount < current_bid:
            messages.error(
                request, "Your bid must be higher than the current bid.")
            return redirect('listing_detail', listing_id=listing.id)

        new_bid = Bids.objects.create(
            listing=listing,
            bidder=request.user,
            bid_amount=bid_amount
        )
        messages.success(request, f"Your bid of ${bid_amount} was placed.")
        return redirect('listing_detail', listing_id=listing.id)

    if request.method == "POST" and 'close_auction' in request.POST:
        if listing.owner == request.user:
            listing.is_active = False
            listing.save()
            messages.success(
                request, "Auction closed. The highest bidder wins!")
        else:
            messages.error(request, "You are not the owner of this listing.")
        return redirect('listing_detail', listing_id=listing.id)

    if request.method == "POST" and 'comment' in request.POST:
        comment_content = request.POST.get("comment_content")
        if comment_content:
            Comments.objects.create(
                listing=listing,
                commenter=request.user,
                content=comment_content
            )
            messages.success(request, "Your comment was added.")
        return redirect('listing_detail', listing_id=listing.id)

    comments = Comments.objects.filter(listing=listing).order_by('-created_at')

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "highest_bid": highest_bid,
        "comments": comments,
        "current_bid": current_bid,
        "is_owner": listing.owner == request.user,
        "is_winner": highest_bid and highest_bid.bidder == request.user,
        "is_watchlisted": request.user in listing.watchlist.all() if request.user.is_authenticated else False
    })


@login_required
def watchlist(request):
    watchlist_items = Listings.objects.filter(watchlist=request.user)

    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listings.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
