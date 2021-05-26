from django.contrib import admin
from django.db.models import Max
from django.urls import reverse
from .models import User, Category, Product, Comment, Bids, Auction

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_prods')

    def get_prods(self, obj):
        prods = obj.product.all()
        return prods

class ProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', "title", 'description', 'img')
    filter_horizontal = ('category',)

class BidsAdmin(admin.ModelAdmin):
    list_display = ("id",'user', "auction", "get_seller", 'bid', "get_current_bid",'bids_time')

    def get_seller(self, obj):
        seller = obj.auction.product.user
        return seller
    get_seller.short_description = 'Seller'

    def get_current_bid(self, obj):
        current_bid = obj.auction.bids_item.all().aggregate(Max('bid'))['bid__max']
        return current_bid
    get_current_bid.short_description = 'Current bid'

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('product',"get_seller", 'start_price', 'finish_price', 'start_date', 'finish_date', 'winner', 'auction_is_active', 'notification' )
    list_display_links = ('product',"get_seller", 'winner')

    def get_seller(self, obj):
        seller = Product.objects.get(prod_auction=obj).user
        return seller
    get_seller.short_description = 'Seller'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_auction_name', 'comment')

    def get_auction_name(self, obj):
        print(obj.auction)
        return obj.auction.product.name
    get_auction_name.short_description = 'Product'



admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(User)
