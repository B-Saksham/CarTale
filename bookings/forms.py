from django import forms
from .models import TestDriveBooking

class TestDriveBookingForm(forms.ModelForm):
    class Meta:
        model = TestDriveBooking
        fields = ['name', 'phone', 'preferred_date', 'preferred_time']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
        }
