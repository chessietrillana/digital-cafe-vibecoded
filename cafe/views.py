from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddToCartForm
from .models import CartItem, Order, OrderLine, Product


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


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    total = sum((item.subtotal() for item in cart_items), start=0)
    return render(
        request, "cafe/cart.html", {"cart_items": cart_items, "total": total}
    )


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    if request.method != "POST":
        return redirect("cart")

    try:
        quantity = int(request.POST.get("quantity", ""))
    except ValueError:
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart")

    if quantity < 1:
        cart_item.delete()
        messages.success(request, f"Removed {cart_item.product.name} from your cart.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Updated {cart_item.product.name} quantity.")
    return redirect("cart")


@login_required
def checkout(request):
    if request.method != "POST":
        return redirect("cart")

    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    with transaction.atomic():
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderLine.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
            )
        cart_items.delete()

    messages.success(request, "Your order has been placed.")
    return redirect("order_history")


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("orderline_set")
    )
    return render(request, "cafe/order_history.html", {"orders": orders})
