from django.urls import path
from .views import sell_car

urlpatterns = [
    path('', sell_car, name='sell_car'),
]