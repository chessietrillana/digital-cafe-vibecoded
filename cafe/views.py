from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddToCartForm
from .models import CartItem, Product


@login_required
def home(request):
    products = Product.objects.filter(is_active=True).order_by("name")
    greeting_name = request.user.first_name or request.user.username
    return render(
        request,
        "cafe/home.html",
        {"products": products, "greeting_name": greeting_name},
    )


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = AddToCartForm()
    return render(
        request, "cafe/product_detail.html", {"product": product, "form": form}
    )


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method != "POST":
        return redirect("product_detail", pk=pk)

    if not product.is_active:
        messages.error(request, f"{product.name} is not currently available.")
        return redirect("product_detail", pk=pk)

    form = AddToCartForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid quantity.")
        return redirect("product_detail", pk=pk)

    quantity = form.cleaned_data["quantity"]
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product, defaults={"quantity": quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"Added {quantity} x {product.name} to your cart.")
    return redirect("product_detail", pk=pk)
