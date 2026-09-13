from django.contrib import admin
from django.utils.html import format_html

from .models import CartItem, Order, OrderLine, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;">',
            obj.image.url,
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "added_at")
    list_filter = ("user",)


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "total")
    list_filter = ("user",)
    inlines = [OrderLineInline]

    @admin.display(description="Total")
    def total(self, obj):
        return obj.total()


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "unit_price", "quantity")
    list_filter = ("order",)
