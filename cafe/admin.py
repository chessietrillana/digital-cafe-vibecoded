from django.contrib import admin

from .models import CartItem, Order, OrderLine, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


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
