from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
]
