from django.urls import path
from .views import NoutbookListCreateView, NoutbookRetrieveUpdateDestroyView
from . import views

urlpatterns = [
    path('noutbooks/', NoutbookListCreateView.as_view(), name='noutbook-list-create'),
    path('noutbooks/<int:pk>/', NoutbookRetrieveUpdateDestroyView.as_view(), name='noutbook-detail'),
    path('add-to-card/<int:product_id>/', views.add_to_card, name='add_to_card'),
    path('delete-from-card/<int:product_id>/', views.delete_from_card, name='delete_from_card'),
    path('get-card/', views.get_card, name='get_card'),
    path('create-order/', views.create_order, name='create_order'),
    path('get-order/<int:order_id>/', views.get_order, name='get_order'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('add-like/<int:product_id>/', views.add_like, name='add_like'),
    path('delete-like/<int:product_id>/', views.delete_like, name='delete_like'),
    path('get-liked-products/', views.get_liked_products, name='get_liked_products'),
]