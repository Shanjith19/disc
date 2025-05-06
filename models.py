from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Discount(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    percentage = models.IntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    shopkeeper = models.ForeignKey(User, related_name='shopkeeper_discounts', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discounts = models.ManyToManyField(Discount)
    total_amount = models.FloatField(default=0.0)

    def calculate_total(self):
        self.total_amount = sum([discount.percentage for discount in self.discounts.all()])
        self.save()

    def __str__(self):
        return f"Cart of {self.user.username}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ Add this
    status = models.CharField(max_length=50, default='Pending')  # ✅ Add this

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id}"
