from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Product


@login_required
def home(request):
    products = Product.objects.filter(is_active=True).order_by("name")
    greeting_name = request.user.first_name or request.user.username
    return render(
        request,
        "cafe/home.html",
        {"products": products, "greeting_name": greeting_name},
    )
