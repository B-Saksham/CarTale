from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cars.models import Car
from blog.models import Blog


def home(request):
    featured_cars = (
        Car.objects
        .filter(is_available=True)
        .order_by('-price')[:3]
    )

    latest_blogs = Blog.objects.order_by('-created_at')[:3]

    return render(request, "pages/home.html", {
        "featured_cars": featured_cars,
        "latest_blogs": latest_blogs,
    })


@login_required
def about(request):
    return render(request, "pages/about.html")


@login_required
def contact(request):
    return render(request, "pages/contact.html")