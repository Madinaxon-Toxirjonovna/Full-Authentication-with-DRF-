from rest_framework import generics 
from product.models import Noutbooks, Card, Order, Like
from .serializers import NoutbooksSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

class NoutbookListCreateView(generics.ListCreateAPIView):
    queryset = Noutbooks.objects.all()
    serializer_class = NoutbooksSerializer

class NoutbookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Noutbooks.objects.all()
    serializer_class = NoutbooksSerializer

def add_to_card(request, product_id):
    card, created = Card.objects.get_or_create(user=request.user)
    card.products.add(product_id) 
    return JsonResponse({"message": "Product added to card."}, status=200)

def delete_from_card(request, product_id):
    card = get_object_or_404(Card, user=request.user)
    card.products.remove(product_id)
    return JsonResponse({"message": "Product removed from card."}, status=200)

def get_card(request):
    card = get_object_or_404(Card, user=request.user)
    products_in_card = card.products.all()  
    return JsonResponse({"products": [product.name for product in products_in_card]}, status=200)

def create_order(request):
    card = get_object_or_404(Card, user=request.user)
    total_amount = sum(product.price for product in card.products.all())  
    order = Order.objects.create(user=request.user, total_amount=total_amount)
    card.products.clear()  
    return JsonResponse({"message": f"Order {order.id} created successfully."}, status=200)

def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return JsonResponse({
        "order_id": order.id,
        "total_amount": order.total_amount,
        "status": order.status
    }, status=200)

def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Completed'  
    order.save()
    return JsonResponse({"message": "Order accepted."}, status=200)

def add_like(request, product_id):
    product = get_object_or_404(Product, id=product_id) 
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if not created:
        return JsonResponse({"message": "You already liked this product."}, status=400)
    return JsonResponse({"message": "Product liked."}, status=200)

def delete_like(request, product_id):
    like = get_object_or_404(Like, user=request.user, product_id=product_id)
    like.delete()
    return JsonResponse({"message": "Product unliked."}, status=200)

def get_liked_products(request):
    likes = Like.objects.filter(user=request.user)
    liked_products = [like.product.name for like in likes]
    return JsonResponse({"liked_products": liked_products}, status=200)
