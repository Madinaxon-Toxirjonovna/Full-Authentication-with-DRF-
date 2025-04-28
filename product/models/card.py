from django.utils import timezone
from django.db import models
from authapp.models import CustomUser
from product.models.products import Noutbooks


class Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Noutbooks, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=None)
  

    def save(self, *args, **kwargs):
        if self.product:
            self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.product}"


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Noutbooks, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=None)
  

    def save(self, *args, **kwargs):
        if self.like:
            self.dislike = False
        elif self.dislike:
            self.like = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.product}"