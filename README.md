# Car Tale

A web-based reconditioned car marketplace built for the Nepal market.
Final Year Project — CS6P05NP | Informatics College Pokhara | London Metropolitan University

**Student:** Saksham Basnet | LMU ID: 23048911  
**Supervisor:** Mrs. Pratibha Gurung

---

## Tech Stack

- **Backend:** Django 6, Python
- **Database:** MySQL (recondition_db)
- **Frontend:** Bootstrap 5, HTML, CSS, JavaScript
- **Payments:** Khalti ePay v2, Stripe Checkout
- **Notifications:** Telegram Bot API

## Features

- Car catalogue with 5-parameter filter system
- Test drive booking with Telegram notifications
- Sell car request with multi-image upload
- Accessories e-commerce store with dual payment gateway
- AI-style guided chatbot (browse, book, sell flows)
- Blog module with auto-slug URLs
- Role-based admin panel (Django admin)

## Setup

1. Clone the repo
2. Create a `.env` file with the following keys:
3. SECRET_KEY=
DB_PASSWORD=
KHALTI_PUBLIC_KEY=
KHALTI_SECRET_KEY=
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

## Notes

- Requires MySQL — create database `recondition_db` before migrating
- Khalti runs in sandbox mode (dev.khalti.com)
- Never commit the `.env` file
