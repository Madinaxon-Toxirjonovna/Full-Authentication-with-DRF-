from django.urls import path
from .views import Posts, CreateProduct

urlpatterns = [
    path('', Posts.as_view()),
    path('create', CreateProduct.as_view())
]