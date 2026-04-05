from django import forms
from .models import SellCarRequest


class SellCarForm(forms.ModelForm):
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = SellCarRequest
        fields = [
            'owner_name',
            'phone',
            'car_brand',
            'car_model',
            'year',
            'mileage',
            'inspection_type',
            'preferred_date'
        ]