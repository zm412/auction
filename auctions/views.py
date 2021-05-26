from django.contrib.auth import authenticate, login, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import timedelta, datetime
from django.db.models import Max
from django import forms
from .models import User, Category, Product, Comment, Bids, Auction
from django.contrib.auth.decorators import login_required


def get_categories():
    category_list = Category.objects.all()
    list = []
    for a in category_list:
        list.append((a.name, a.name))
    return tuple(list)


class Add_product(forms.ModelForm):
    start_price = forms.CharField()
    category = forms.MultipleChoiceField(required=False,widget=forms.SelectMultiple,choices=get_categories())
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':23, 'rows': 3}))

    class Meta:
        model = Product
        fields = ['name', 'title', 'description', 'img']



def index(request):
    active_auction_list = Auction.objects.filter(auction_is_active=True)

    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(active_auction_list, 'Active listings')
    )

def all_lists(request):
    all_auction_list = Auction.objects.all()

    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(all_auction_list, 'All listings')
    )

def category(request, category_name):
    if category_name == 'Out of categories':
        this_category_auctions = Auction.objects.filter(product__category=None)
        title = f'Products out of categories'
    else:
        this_category_auctions = Auction.objects.filter(product__category__name=category_name).filter(auction_is_active=True)
        title = f'Products from {category_name} category'

    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(this_category_auctions, title)
    )


def collect_info_for_index(my_list, title):
    context = []

    for auction in my_list:
       current_bid = auction.bids_item.all().aggregate(Max('bid'))['bid__max']
       context.append({
           "auction": auction,
           "current_bid": current_bid,
           'img': auction.product.img or 'noImage.jpeg'
       })
    return {
        "title": title,
        "auction_list": context,
        'category_list': Category.objects.all()
    }

@login_required
def my_items(request, user_id):
    user = User.objects.get(id=user_id)
    users_auctions = Auction.objects.filter(product__user=user)
    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(users_auctions, 'My items')
    )

@login_required
def my_purchases(request, user_id):
    user = User.objects.get(id=user_id)
    users_auctions = Auction.objects.filter(winner=user)
    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(users_auctions, 'My purchases')
    )


def current_bid_func(auction, max):
    if max != None:
        return auction.bids_item.get(bid=max)
    else:
        return False

def get_prod_context(auction_id, user_id=0, message=''):
    auction = Auction.objects.get(id=auction_id)
    max_bid = auction.bids_item.all().aggregate(Max('bid'))['bid__max']
    seller_id = auction.product.user.id
    watchlist_count = auction.wish_list_users.all().count()
    context = {
        "auction": auction,
        "user_id": user_id,
        'if_in_wish': auction.wish_list_users.filter(id=user_id).exists(),
        "comments": auction.comm_item.all(),
        "is_not_seller": True,
        "current_bid": current_bid_func(auction, max_bid),
        'count_bids':auction.bids_item.all().count(),
        'watchers': watchlist_count,
        'category_list': Category.objects.all(),
        'message': message,
        'img': auction.product.img or 'noImage.jpeg'
    }
    if int( user_id ) > 0:
        context.update({'is_not_seller':int(user_id) != seller_id})
    return context

@login_required
def add_comment(request, auction_id, user_id=0):
    if request.method == "POST":
        auction = Auction.objects.get(id=auction_id)
        comment = auction.comm_item.create(
                user = User.objects.get(id=user_id),
                comment = request.POST['comment'],
            )
    return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction.id)))

def show_prod(request, auction_id, user_id=0):

    auction = Auction.objects.get(id=auction_id)
    context = get_prod_context(auction_id, user_id)
    return render(request, 'auctions/product.html', context)
"""
def show_prod(request, auction_id, user_id=0):

    auction = Auction.objects.get(id=auction_id)
    context = get_prod_context(auction_id, user_id)

    if request.method == "POST":
        comment = auction.comm_item.create(
            user = User.objects.get(id=user_id),
            comment = request.POST['comment'],
        )
        return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction.id)))

    return render(request, 'auctions/product.html', context)

"""

@login_required
def show_wishes(request, user_id):
    current_wish_list = Auction.objects.filter(wish_list_users__id=user_id)

    return render(
        request,
        'auctions/index.html',
        collect_info_for_index(current_wish_list, 'Products from your wish list')
    )

@login_required
def make_bid(request, user_id, auction_id):
    auction = Auction.objects.get(id=auction_id)
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        bid = request.POST['item_bid']
        checkingBid = checkBid(bid, auction_id)

        if  checkingBid == 'is_ok':
            auction.bids_item.create(
                bid=bid,
                user=user,
                bids_time=datetime.now(),
            )
            return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction_id)))
        else:
            context = get_prod_context(auction_id, user_id, checkingBid)
            return render(request, 'auctions/product.html', context)


    return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction_id)))

def checkBid(bid, auction_id):

    auction = Auction.objects.get(id=auction_id)
    bids = auction.bids_item.all()
    max_bid = auction.bids_item.all().aggregate(Max('bid'))['bid__max']
    message = 'is_ok'
    if max_bid:
        if int(bid) <= max_bid:
            message = f'Your bid should be larger then {max_bid}'
    else :
        if int(bid) < auction.start_price:
            message = f'Your bid should be larger or equal then {auction.start_price}'
    return message

def put_in(request, user_id):
    user = User.objects.get(id=user_id)
    category_list = Category.objects.all()
    form = Add_product()

    if request.method == "POST":
        new_product = Product(user=user)
        new_product.save()

        category_item = request.POST.getlist('category')

        add_form = Add_product(request.POST, request.FILES, instance=new_product)

        if add_form.is_valid():
            product = add_form.save()
            product.save()

            for c in category_item:
                categoryC = Category.objects.get(name=c)
                categoryC.item_category.add(product)

            auction = Auction(
                product=product,
                start_price = request.POST['start_price'],
                start_date = datetime.now(),
                finish_date = datetime.now()+timedelta(2)
            )
            auction.save()
            add_form = Add_product()
            return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction.id)))
        else:
            return render(request, 'auctions/add_prod.html', {
                "form": form,
                "username": user,
            })
    else:
        return render(request, 'auctions/add_prod.html', {
            "form": form,
            "username": user,
        })

@login_required
def finish_trade(request, user_id, auction_id):
    user = User.objects.get(id=user_id)
    auction = Auction.objects.get(id=auction_id)
    if auction.bids_item.all().count() > 0:
        max_bid = auction.bids_item.all().aggregate(Max('bid'))['bid__max']
        winner_note_bid = auction.bids_item.get(bid=max_bid)
        auction.finish_price = max_bid
        auction.finish_date = datetime.now()
        auction.auction_is_active = False
        auction.winner = winner_note_bid.user
        auction.notification = True

        auction.save(update_fields=[
            'finish_price',
            'finish_date',
            'auction_is_active',
            'winner',
            'notification'
        ])
    else:
        auction.finish_price = 0
        auction.finish_date = datetime.now()
        auction.auction_is_active = False
        auction.winner = None
        auction.save(update_fields=[
            'finish_price',
            'finish_date',
            'auction_is_active',
            'winner'
        ])
    return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction_id)))

@login_required
def add_in_list(request, user_id, auction_id):
    user = User.objects.get(id=user_id)
    auction = Auction.objects.get(id=auction_id)
    auction.wish_list_users.add(user)

    return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction_id)))

@login_required
def remove_from_list(request, user_id, auction_id):
    user = User.objects.get(id=user_id)
    auction = Auction.objects.get(id=auction_id)
    auction.wish_list_users.remove(user)

    return HttpResponseRedirect(reverse("show_prod", args=(user_id, auction_id)))

@login_required
def aside_notification(request, auction_id):
    return HttpResponseRedirect(reverse("index"))

@login_required
def no_notification(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    auction.notification = False
    auction.save(update_fields=['notification',])

    return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            notifications = Auction.objects.filter(winner=user).filter(notification=True)
            print(notifications, 'notes')
            if len(notifications) > 0:
                active_auction_list = Auction.objects.filter(auction_is_active=True)
                context = collect_info_for_index(active_auction_list, 'Active listings')
                context['notifications'] = notifications

                return render(request, 'auctions/index.html', context)
            else:
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
