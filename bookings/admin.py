from django.contrib import admin
from .models import TestDriveBooking

@admin.register(TestDriveBooking)
class TestDriveBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'car', 'preferred_date', 'preferred_time')
    list_filter = ('preferred_date',)
