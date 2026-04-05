from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")