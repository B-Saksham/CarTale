from django.contrib import admin
from django.utils.html import format_html
from .models import SellCarRequest, SellCarImage


class SellCarImageInline(admin.TabularInline):
    model = SellCarImage
    extra = 0
    readonly_fields = ("image_preview",)
    fields = ("image", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; border:1px solid #ddd;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Preview"


@admin.register(SellCarRequest)
class SellCarRequestAdmin(admin.ModelAdmin):
    list_display = (
        "owner_name",
        "car_brand",
        "car_model",
        "inspection_type",
        "preferred_date",
        "image_count",
    )
    list_filter = ("inspection_type", "preferred_date")
    inlines = [SellCarImageInline]

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = "Images"
