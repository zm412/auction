from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass
    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    category = models.ManyToManyField(Category,blank=True, null=True, related_name="item_category")
    title = models.CharField(max_length=64)
    name = models.CharField(max_length=130)
    description = models.CharField(max_length=2000)
    img = models.ImageField(upload_to='images', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Auction(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="prod_auction")
    auction_is_active = models.BooleanField(default=True)
    start_price = models.PositiveIntegerField()
    finish_price  = models.PositiveIntegerField(blank=True, null=True)
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField()
    wish_list_users = models.ManyToManyField(User, blank=True, related_name="wish_list")
    winner = models.ForeignKey(User, blank=True, null=True,on_delete=models.CASCADE, related_name="winner")
    notification = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comm_item")
    comment = models.CharField(max_length=2000)

    def __str__(self):
        return f"user: {self.user}, auction: {self.auction}, comment: {self.comment}"

class Bids(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids_item")
    bid = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    bids_time = models.DateTimeField()

    def __str__(self):
        return f"auction: {self.auction}, bid: {self.bid}, user: {self.user}, bids time: {self.bids_time}"

