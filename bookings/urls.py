from django.urls import path
from .views import book_test_drive

urlpatterns = [
    path('book/<int:car_id>/', book_test_drive, name='book_test_drive'),
]
