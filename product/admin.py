from django.contrib import admin
from product.models import Noutbooks, Category
from product.models.order import Order
from product.models.card import Card, Like

admin.site.register(Noutbooks)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Card)
admin.site.register(Like)