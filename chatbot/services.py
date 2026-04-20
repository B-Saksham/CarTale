from cars.models import Car
from bookings.forms import TestDriveBookingForm
from sell_requests.forms import SellCarForm
from sell_requests.views import send_telegram_alert
from datetime import datetime, timedelta


def reset_chat(request):
    request.session["chatbot"] = {
        "flow": None,
        "step": "start",
        "data": {}
    }


def handle_chatbot_logic(request, message, files=None):
    state = request.session.get("chatbot")

    # FIRST LOAD
    if not state or not message:
        reset_chat(request)
        return {
            "reply": " Welcome to CarTale! How Can We Assist You?",
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

        # ================= CAR =================
        if step == "car":
            car_id = int(message.split(":")[0])
            data["car"] = car_id
            state["step"] = "name"
            request.session.modified = True
            return {"reply": "Enter your name:"}

        # ================= NAME =================
        elif step == "name":
            data["name"] = message
            state["step"] = "phone"
            request.session.modified = True
            return {"reply": "Enter phone number:"}

        # ================= PHONE =================
        elif step == "phone":
            data["phone"] = message
            state["step"] = "date"
            request.session.modified = True

            return {
                "reply": "Select preferred date:",
                "options": ["Today", "Tomorrow", "Pick another date"]
            }

        # ================= HANDLE MANUAL DATE TRIGGER =================
        if message == "Pick another date":
            return {"reply": "Enter date (YYYY-MM-DD):"}

        # ================= DATE =================
        elif step == "date":

            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            if message == "Today":
                selected_date = today
            elif message == "Tomorrow":
                selected_date = tomorrow
            else:
                # manual input
                try:
                    selected_date = datetime.strptime(message, "%Y-%m-%d").date()
                except:
                    return {
                        "reply": "Invalid format. Use YYYY-MM-DD or select an option.",
                        "options": ["Today", "Tomorrow", "Pick another date"]
                    }

            data["preferred_date"] = str(selected_date)
            state["step"] = "time"

            # ================= TIME SLOTS =================
            now = datetime.now()

            if selected_date == now.date():
                start_hour = max(9, now.hour + 1)
            else:
                start_hour = 9

            time_options = [f"{h:02d}:00" for h in range(start_hour, 20)]

            request.session.modified = True

            return {
                "reply": f"Select time for {selected_date}:",
                "options": time_options
            }

        # ================= TIME =================
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
                    "reply": " Booking successful!",
                    "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
                }

            else:
                return {"reply": f" Invalid data: {form.errors}"}
# ================= SELL FLOW =================

    if flow == "sell":

        # 🔥 IMAGE STEP
        if step == "images":
            return {
                "reply": "Processing images..."
            }

        fields = [
            "owner_name", "phone", "car_brand", "car_model",
            "year", "mileage", "inspection_type", "preferred_date"
        ]

        for field in fields:

            if field in data:
                continue

            # ✅ FIXED INSPECTION TYPE HANDLING
            if field == "inspection_type":
                if message == "Home Inspection":
                    data[field] = "home"
                elif message == "Visit Showroom":
                    data[field] = "visit"
                else:
                    return {
                        "reply": "Please select a valid option",
                        "options": ["Home Inspection", "Visit Showroom"]
                    }
            else:
                data[field] = message

            next_index = fields.index(field) + 1

            if next_index < len(fields):
                next_field = fields[next_index]
                state["step"] = next_field
                request.session.modified = True

                if next_field == "inspection_type":
                    return {
                        "reply": "Select inspection type:",
                        "options": ["Home Inspection", "Visit Showroom"]
                    }

                return {"reply": f"Enter {next_field}:"}

            else:
                state["step"] = "images"
                request.session.modified = True

                return {
                    "reply": "Upload car images now (you can select multiple)"
                }
    # FALLBACK
    reset_chat(request)
    return {
        "reply": "⚠️ Something went wrong. Restarting...",
        "options": ["Browse Cars", "Book Test Drive", "Sell Car"]
    }