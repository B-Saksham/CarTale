from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import handle_chatbot_logic

from sell_requests.forms import SellCarForm
from sell_requests.views import send_telegram_alert
from sell_requests.models import SellCarImage


@csrf_exempt
def chatbot_api(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"})

    message = request.POST.get("message")

    # ================= IMAGE UPLOAD (FINAL SELL STEP) =================
    if request.FILES and request.FILES.getlist("images"):

        form = SellCarForm(request.POST, request.FILES)

        if form.is_valid():
            sell_request = form.save()

            images = request.FILES.getlist("images")
            saved_images = []

            for img in images:
                image_instance = SellCarImage.objects.create(
                    sell_request=sell_request,
                    image=img
                )
                saved_images.append(image_instance.image)

            message_text = (
                f"New Sell Request\n\n"
                f"Owner: {sell_request.owner_name}\n"
                f"Phone: {sell_request.phone}\n"
                f"Car: {sell_request.car_brand} {sell_request.car_model}\n"
                f"Year: {sell_request.year}\n"
                f"Mileage: {sell_request.mileage}"
            )

            send_telegram_alert(message_text, images=saved_images)

            return JsonResponse({
                "reply": " Sell request submitted successfully!",
                "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
            })

        return JsonResponse({
            "reply": f"❌ Error: {form.errors}"
        })

    # ================= NORMAL CHAT FLOW =================
    response = handle_chatbot_logic(request, message)

    return JsonResponse(response)