from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/add/", views.add_to_cart, name="add_to_cart"),
]
