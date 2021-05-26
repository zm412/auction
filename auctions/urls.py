from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("all_lists", views.all_lists, name="all_lists"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category/<str:category_name>", views.category, name='category'),
    path("<int:user_id>/put_in", views.put_in, name="put_in"),
    path("<int:user_id>/my_purchases", views.my_purchases, name="my_purchases"),
    path("<int:user_id>/my_items", views.my_items, name="my_items"),
    path("<int:user_id>/wish_list", views.show_wishes, name="show_wishes"),
    path("<int:user_id>/<int:auction_id>", views.show_prod, name="show_prod"),
    path("<int:user_id>/<int:auction_id>/finish_trade", views.finish_trade, name="finish_trade"),
    path("<int:user_id>/<int:auction_id>/make_bid", views.make_bid, name="make_bid"),
    path("<int:user_id>/<int:auction_id>/add_in_list", views.add_in_list, name="add_in_list"),
    path("<int:user_id>/<int:auction_id>/remove_from_list", views.remove_from_list, name="remove_from_list"),
    path("<int:user_id>/<int:auction_id>/add_comment", views.add_comment, name="add_comment"),
    path("<int:auction_id>/notifi", views.aside_notification, name="aside_notification"),
    path("<int:auction_id>/no_notifi", views.no_notification, name="no_notification"),
   # path("products/<int:product_id>", views.show_prod, name='show_prod')
]
