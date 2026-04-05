from django.contrib import admin
from .models import Car, CarImage


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price', 'fuel_type', 'is_available')
    list_filter = ('fuel_type', 'transmission', 'is_available')
    search_fields = ('brand', 'model')
    inlines = [CarImageInline]
