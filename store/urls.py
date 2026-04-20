from django.urls import path
from .views import (
    product_list, add_to_cart, cart_view, remove_from_cart,
    update_cart, buy_now, checkout, khalti_verify, payment_success, stripe_create_session, stripe_success
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),

    path('cart/', cart_view, name='cart_view'),
    path('checkout/', checkout, name='checkout'),

    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/<str:action>/', update_cart, name='update_cart'),

    path('khalti-verify/', khalti_verify, name='khalti_verify'),
    path('success/', payment_success, name='payment_success'),

    path('stripe/create/<int:order_id>/', stripe_create_session, name='stripe_create_session'),
    path('stripe-success/<int:order_id>/', stripe_success, name='stripe_success'),
]