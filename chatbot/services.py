from cars.models import Car
from bookings.forms import TestDriveBookingForm
from sell_requests.forms import SellCarForm


def reset_chat(request):
    request.session["chatbot"] = {
        "flow": None,
        "step": "start",
        "data": {}
    }


def handle_chatbot_logic(request, message):
    state = request.session.get("chatbot")

    # FIRST LOAD
    if not state or not message:
        reset_chat(request)
        return {
            "reply": "👋 Welcome to CarTale! What would you like to do?",
            "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
        }

    flow = state["flow"]
    step = state["step"]
    data = state["data"]

    # ================= GLOBAL OPTIONS =================

    if message == "Yes, Book Now":
        state["flow"] = "booking"
        state["step"] = "car"
        request.session.modified = True

        filtered_ids = request.session.get("filtered_cars")

        if filtered_ids:
            cars = Car.objects.filter(id__in=filtered_ids)
        else:
            cars = Car.objects.filter(is_available=True)

        return {
            "reply": "Select a car to book:",
            "options": [f"{c.id}:{c.brand} {c.model}" for c in cars]
        }

    if message == "No, Start Over":
        reset_chat(request)
        return {
            "reply": "What would you like to do?",
            "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
        }

    # ================= START =================

    if step == "start":
        if message == "Browse Cars":
            state["flow"] = "browse"
            state["step"] = "budget"
            request.session.modified = True

            return {
                "reply": "Select your budget:",
                "options": [
                    "under_2000000",
                    "2000000_3500000",
                    "3500000_5000000",
                    "over_5000000"
                ]
            }

        elif message == "Book Test Drive":
            state["flow"] = "booking"
            state["step"] = "car"
            request.session.modified = True

            cars = Car.objects.filter(is_available=True)

            return {
                "reply": "Select a car:",
                "options": [f"{c.id}:{c.brand} {c.model}" for c in cars]
            }

        elif message == "Sell Car":
            state["flow"] = "sell"
            state["step"] = "owner_name"
            request.session.modified = True
            return {"reply": "Enter your name:"}

    # ================= BROWSE FLOW =================

    if flow == "browse":

        cars = Car.objects.filter(is_available=True)

        # APPLY FILTERS
        if data.get("price"):
            if data["price"] == "under_2000000":
                cars = cars.filter(price__lt=2000000)
            elif data["price"] == "2000000_3500000":
                cars = cars.filter(price__gte=2000000, price__lte=3500000)
            elif data["price"] == "3500000_5000000":
                cars = cars.filter(price__gte=3500000, price__lte=5000000)
            elif data["price"] == "over_5000000":
                cars = cars.filter(price__gt=5000000)

        if data.get("brand"):
            cars = cars.filter(brand=data["brand"])

        if data.get("fuel_type"):
            cars = cars.filter(fuel_type=data["fuel_type"])

        if data.get("transmission"):
            cars = cars.filter(transmission=data["transmission"])

        # ---------- STEPS ----------

        if step == "budget":
            data["price"] = message
            state["step"] = "brand"
            request.session.modified = True

            # 🔥 REBUILD QUERY WITH NEW FILTER
            filtered_cars = Car.objects.filter(is_available=True)

            if message == "under_2000000":
                filtered_cars = filtered_cars.filter(price__lt=2000000)
            elif message == "2000000_3500000":
                filtered_cars = filtered_cars.filter(price__gte=2000000, price__lte=3500000)
            elif message == "3500000_5000000":
                filtered_cars = filtered_cars.filter(price__gte=3500000, price__lte=5000000)
            elif message == "over_5000000":
                filtered_cars = filtered_cars.filter(price__gt=5000000)

            brands = filtered_cars.values_list("brand", flat=True).distinct()

            return {
                "reply": "Select brand:",
                "options": list(brands)
            }
        elif step == "brand":
            data["brand"] = message
            state["step"] = "fuel"
            request.session.modified = True

            fuels = cars.values_list("fuel_type", flat=True).distinct()

            return {
                "reply": "Fuel type:",
                "options": list(fuels)
            }

        elif step == "fuel":
            data["fuel_type"] = message
            state["step"] = "transmission"
            request.session.modified = True

            transmissions = cars.values_list("transmission", flat=True).distinct()

            return {
                "reply": "Transmission:",
                "options": list(transmissions)
            }

        elif step == "transmission":
            data["transmission"] = message
            request.session.modified = True

            # FINAL RESULTS
            car_data = [
                {
                    "id": c.id,
                    "brand": c.brand,
                    "model": c.model,
                    "year": c.year,
                    "price": c.price
                }
                for c in cars
            ]

            request.session["filtered_cars"] = [c.id for c in cars]

            return {
                "reply": "Here are matching cars. Would you like to book one?",
                "cars": car_data,
                "options": ["Yes, Book Now", "No, Start Over"]
            }

    # ================= BOOKING FLOW =================

    if flow == "booking":

        if step == "car":
            car_id = int(message.split(":")[0])
            data["car"] = car_id
            state["step"] = "name"
            request.session.modified = True
            return {"reply": "Enter your name:"}

        elif step == "name":
            data["name"] = message
            state["step"] = "phone"
            request.session.modified = True
            return {"reply": "Enter phone number:"}

        elif step == "phone":
            data["phone"] = message
            state["step"] = "date"
            request.session.modified = True
            return {"reply": "Preferred date (YYYY-MM-DD):"}

        elif step == "date":
            data["preferred_date"] = message
            state["step"] = "time"
            request.session.modified = True
            return {"reply": "Preferred time (HH:MM):"}

        elif step == "time":
            data["preferred_time"] = message

            form_data = {
                "name": data["name"],
                "phone": data["phone"],
                "preferred_date": data["preferred_date"],
                "preferred_time": data["preferred_time"],
            }

            form = TestDriveBookingForm(form_data)

            if form.is_valid():
                booking = form.save(commit=False)
                booking.car_id = data["car"]
                booking.save()

                # TELEGRAM ALERT
                from bookings.views import send_telegram_alert

                car = Car.objects.get(id=data["car"])

                msg = (
                    f"New Test Drive Booking\n\n"
                    f"Car: {car.brand} {car.model}\n"
                    f"User: {request.user.username}\n"
                    f"Date: {booking.preferred_date}\n"
                    f"Time: {booking.preferred_time}\n"
                    f"Phone: {booking.phone}"
                )

                send_telegram_alert(msg)

                reset_chat(request)

                return {
                    "reply": "✅ Booking successful!",
                    "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
                }

            else:
                return {"reply": f"❌ Invalid data: {form.errors}"}

    # ================= SELL FLOW =================

    if flow == "sell":
        fields = [
            "owner_name", "phone", "car_brand", "car_model",
            "year", "mileage", "inspection_type", "preferred_date"
        ]

        for field in fields:
            if field not in data:
                data[field] = message
                next_index = fields.index(field) + 1

                if next_index < len(fields):
                    state["step"] = fields[next_index]
                    request.session.modified = True
                    return {"reply": f"Enter {fields[next_index]}:"}

                else:
                    form = SellCarForm(data)
                    if form.is_valid():
                        form.save()
                        reset_chat(request)
                        return {
                            "reply": "✅ Sell request submitted!",
                            "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
                        }
                    else:
                        return {"reply": f"❌ Error: {form.errors}"}

    # FALLBACK
    reset_chat(request)
    return {
        "reply": "⚠️ Something went wrong. Restarting...",
        "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
    }