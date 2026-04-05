from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Blog


@login_required
def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by("-created_at")

    return render(request, "blog/blog_list.html", {
        "blogs": blogs
    })


@login_required
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_published=True)

    return render(request, "blog/blog_detail.html", {
        "blog": blog
    })