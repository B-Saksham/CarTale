from django.urls import path
from .views import car_list, car_detail

urlpatterns = [
    path('', car_list, name='car_list'),
    path('car/<int:car_id>/', car_detail, name='car_detail'),
]
