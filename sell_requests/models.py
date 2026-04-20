from django.db import models


class SellCarRequest(models.Model):
    INSPECTION_CHOICES = (
        ('visit', 'Home Visit'),
        ('bring', 'Visi Showroom'),
    )

    owner_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    car_brand = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_CHOICES)
    preferred_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner_name} - {self.car_brand} {self.car_model}"


class SellCarImage(models.Model):
    sell_request = models.ForeignKey(
        SellCarRequest,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="sell_cars/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.sell_request}"
