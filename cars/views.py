from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car


@login_required
def car_list(request):
    
    cars = Car.objects.filter(is_available=True)

    # ---------- AVAILABLE FILTER OPTIONS (FROM DB) ----------
    available_brands = (
        Car.objects.filter(is_available=True)
        .values_list("brand", flat=True)
        .distinct()
    )

    available_years = (
        Car.objects.filter(is_available=True)
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    # ---------- SELECTED FILTERS ----------
    selected_brands = request.GET.getlist("brand")
    selected_fuel = request.GET.getlist("fuel_type")
    selected_transmission = request.GET.getlist("transmission")
    selected_years = request.GET.getlist("year")
    selected_price = request.GET.getlist("price")

    # ---------- APPLY FILTERS ----------
    if selected_brands:
        cars = cars.filter(brand__in=selected_brands)

    if selected_fuel:
        cars = cars.filter(fuel_type__in=selected_fuel)

    if selected_transmission:
        cars = cars.filter(transmission__in=selected_transmission)

    if selected_years:
        cars = cars.filter(year__in=selected_years)

    if selected_price:
        price_qs = Car.objects.none()
        for p in selected_price:
            if p == "under_2000000":
                price_qs |= cars.filter(price__lt=2000000)
            elif p == "2000000_3500000":
                price_qs |= cars.filter(price__gte=2000000, price__lte=3500000)
            elif p == "3500000_5000000":
                price_qs |= cars.filter(price__gte=3500000, price__lte=5000000)
            elif p == "over_5000000":
                price_qs |= cars.filter(price__gt=5000000)
        cars = price_qs

    context = {
        "cars": cars,
        "available_brands": available_brands,
        "available_years": available_years,

        # Selected values (for checkbox persistence)
        "selected_brands": selected_brands,
        "selected_fuel": selected_fuel,
        "selected_transmission": selected_transmission,
        "selected_years": selected_years,
        "selected_price": selected_price,
    }
    
    return render(request, "cars/car_list.html", context)


@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, "cars/car_detail.html", {"car": car})
