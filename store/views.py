from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Product, Order, OrderItem
import requests
import uuid


# ================= TELEGRAM ALERT =================

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(
            url,
            data={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=5
        )
    except Exception:
        pass


# ================= CART HELPERS =================

def get_cart(request):
    return request.session.setdefault("cart", {})

def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


# ================= PRODUCT LIST =================
@login_required
def product_list(request):
    products = Product.objects.filter(is_available=True)
    cart = get_cart(request)
    cart_count = sum(item["qty"] for item in cart.values())

    return render(request, "store/product_list.html", {
        "products": products,
        "cart_count": cart_count
    })


# ================= ADD TO CART =================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)

    pid = str(product.id)

    if pid in cart:
        cart[pid]["qty"] += 1
    else:
        cart[pid] = {
            "name": product.name,
            "price": product.price,
            "qty": 1
        }

    save_cart(request, cart)
    messages.success(request, f"{product.name} added to cart")
    return redirect("product_list")


# ================= REMOVE =================
@login_required
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    save_cart(request, cart)
    return redirect("cart_view")


# ================= UPDATE QTY =================
@login_required
def update_cart(request, product_id, action):
    cart = get_cart(request)
    pid = str(product_id)

    if pid in cart:
        if action == "inc":
            cart[pid]["qty"] += 1
        elif action == "dec":
            cart[pid]["qty"] -= 1
            if cart[pid]["qty"] <= 0:
                del cart[pid]

    save_cart(request, cart)
    return redirect("cart_view")


# ================= CART =================
@login_required
def cart_view(request):
    cart = get_cart(request)
    items = []
    total = 0

    for pid, item in cart.items():
        subtotal = item["price"] * item["qty"]
        total += subtotal

        items.append({
            "id": pid,
            "name": item["name"],
            "price": item["price"],
            "qty": item["qty"],
            "subtotal": subtotal
        })

    return render(request, "store/cart.html", {
        "cart_items": items,
        "total": total
    })


# ================= BUY NOW =================
@login_required
def buy_now(request, product_id):
    cart = {}
    product = get_object_or_404(Product, id=product_id)

    cart[str(product.id)] = {
        "name": product.name,
        "price": product.price,
        "qty": 1
    }

    save_cart(request, cart)
    return redirect("checkout")


# ================= CHECKOUT PAGE =================
@login_required
def checkout(request):
    cart = get_cart(request)

    if not cart:
        messages.error(request, "Cart is empty")
        return redirect("product_list")

    total = sum(item["price"] * item["qty"] for item in cart.values())

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            user=request.user,
            customer_name=name,
            phone=phone,
            email=email,
            total_amount=total,
            payment_status="pending",
            payment_method=payment_method
        )

        # Save order items
        # Save order items
        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["qty"],
                price=item["price"]
            )

        # ================= STRIPE =================
        if payment_method == "stripe":
            return redirect("stripe_create_session", order_id=order.id)

        test_amount = 10

        payload = {
            "return_url": "http://127.0.0.1:8000/store/khalti-verify/",
            "website_url": "http://127.0.0.1:8000/",
            "amount": test_amount * 100,
            "purchase_order_id": str(order.id),
            "purchase_order_name": f"Order {order.id}",
            "customer_info": {
                "name": name,
                "email": email,
                "phone": phone
            }
        }

        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers)
        data = response.json()

        if "payment_url" in data:
            order.khalti_pidx = data["pidx"]
            order.save()
            return redirect(data["payment_url"])
        else:
            messages.error(request, "Khalti error. Try again.")
            return redirect("cart_view")

    return render(request, "store/checkout.html", {"total": total})


# ================= VERIFY PAYMENT =================
@login_required
def khalti_verify(request):
    pidx = request.GET.get("pidx")

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"pidx": pidx}

    response = requests.post(settings.KHALTI_VERIFY_URL, json=payload, headers=headers)
    data = response.json()

    order = Order.objects.filter(khalti_pidx=pidx).first()

    if data.get("status") == "Completed":
        order.payment_status = "paid"
        order.save()

        # 🔔 TELEGRAM ALERT FOR SUCCESSFUL ORDER
        items = OrderItem.objects.filter(order=order)

        item_lines = ""
        for item in items:
            item_lines += f"- {item.product.name} × {item.quantity}\n"

        message = (
            f"New Store Order (PAID)\n\n"
            f"Order ID: {order.id}\n"
            f"Customer: {order.customer_name}\n"
            f"Phone: {order.phone}\n"
            f"Email: {order.email}\n\n"
            f"Items:\n{item_lines}\n"
            f"Total: NPR {order.total_amount}"
        )

        send_telegram_alert(message)

        request.session["cart"] = {}
        return redirect("payment_success")

    else:
        order.payment_status = "failed"
        order.save()
        messages.error(request, "Payment failed")
        return redirect("cart_view")


# ================= SUCCESS PAGE =================
@login_required
def payment_success(request):
    return render(request, "store/payment_success.html")

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def stripe_create_session(request, order_id):
    order = Order.objects.get(id=order_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'npr',
                'product_data': {
                    'name': f"Order #{order.id}",
                },
                'unit_amount': order.total_amount * 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"http://127.0.0.1:8000/store/stripe-success/{order.id}/",
        cancel_url="http://127.0.0.1:8000/store/cart/",
    )

    return redirect(session.url)


@login_required
def stripe_success(request, order_id):
    order = Order.objects.get(id=order_id)

    order.payment_status = "paid"
    order.save()

    send_telegram_alert(f"Stripe Payment Success - Order #{order.id}")

    request.session["cart"] = {}

    return redirect("payment_success")