from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .services import handle_chatbot_logic


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        response = handle_chatbot_logic(request, user_message)

        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"})