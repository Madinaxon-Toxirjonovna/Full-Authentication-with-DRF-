from django.utils import timezone
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Category'

    def __str__(self):
        return self.name


class Noutbooks(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(default=None)



    class Meta:
        verbose_name = "Noutbook"
        verbose_name_plural = "Noutbooks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model}"