from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests

from .forms import SellCarForm
from .models import SellCarImage


def send_telegram_alert(message, images=None):
    try:
        # 1️⃣ Send text message
        text_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(
            text_url,
            data={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=5
        )

        # 2️⃣ Send images if provided
        if images:
            for image in images:
                photo_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendPhoto"
                with open(image.path, "rb") as photo:
                    requests.post(
                        photo_url,
                        data={
                            "chat_id": settings.TELEGRAM_CHAT_ID
                        },
                        files={
                            "photo": photo
                        },
                        timeout=10
                    )

    except Exception:
        # Fail silently so main sell request never breaks
        pass


@login_required
def sell_car(request):
    if request.method == "POST":
        form = SellCarForm(request.POST, request.FILES)

        if form.is_valid():
            # ✅ Save main sell request
            sell_request = form.save()

            # 🔔 Prepare Telegram message
            message = (
                f"New Sell Request\n\n"
                f"Owner: {sell_request.owner_name}\n"
                f"Phone: {sell_request.phone}\n"
                f"Car: {sell_request.car_brand} {sell_request.car_model}\n"
                f"Year: {sell_request.year}\n"
                f"Mileage: {sell_request.mileage}"
            )

            # ✅ Save images
            images = request.FILES.getlist("images")
            saved_images = []

            for img in images:
                image_instance = SellCarImage.objects.create(
                    sell_request=sell_request,
                    image=img
                )
                saved_images.append(image_instance.image)

            # 🔔 Send Telegram alert with images
            send_telegram_alert(message, images=saved_images)

            messages.success(
                request,
                "Your sell request has been submitted successfully."
            )
            return redirect("sell_car")

        else:
            print("FORM ERRORS:", form.errors)

    else:
        form = SellCarForm()

    return render(
        request,
        "sell_requests/sell_car.html",
        {"form": form}
    )