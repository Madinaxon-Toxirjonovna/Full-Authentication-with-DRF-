from django.utils import timezone
from django.db import models
from authapp.models import CustomUser
from product.models.card import Card


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card = models.ManyToManyField(Card)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=None)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_price = sum(card.price * card.quantity for card in self.card.all())
        self.price = total_price
        super().save(update_fields=['price'])

    def __str__(self):
        return f"{self.user} - {', '.join(str(card.product.model) for card in self.card.all())}"