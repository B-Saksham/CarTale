from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import requests

from .forms import TestDriveBookingForm
from cars.models import Car


def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
        }
        requests.post(url, data=data, timeout=5)
    except Exception:
        # Fail silently so booking never breaks
        pass


@login_required
def book_test_drive(request, car_id):
    car = Car.objects.get(id=car_id)

    if request.method == 'POST':
        form = TestDriveBookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car
            booking.save()

            # 🔔 TELEGRAM ALERT
            message = (
                f"New Test Drive Booking\n\n"
                f"Car: {car.brand} {car.model}\n"
                f"User: {request.user.username}\n"
                f"Date: {booking.preferred_date}\n"
                f"Time: {booking.preferred_time}\n"
                f"Phone: {booking.phone}"
            )
            send_telegram_alert(message)

            messages.success(
                request,
                "Test Drive booked successfully!"
            )

            return redirect('/')

    else:
        form = TestDriveBookingForm()

    return render(request, 'bookings/book_test_drive.html', {
        'form': form,
        'car': car
    })