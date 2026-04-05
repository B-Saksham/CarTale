from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Order, OrderItem


# ---------- PRODUCT IMAGE INLINE ----------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("preview",)
    fields = ("image", "preview", "order")

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:80px;border-radius:6px;border:1px solid #ccc;" />',
                obj.image.url
            )
        return "No image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('name',)
    inlines = [ProductImageInline]


# ---------- ORDER ITEMS INLINE ----------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "phone",
        "total_amount",
        "payment_status",
        "created_at",
    )
    list_filter = ("payment_status",)
    inlines = [OrderItemInline]