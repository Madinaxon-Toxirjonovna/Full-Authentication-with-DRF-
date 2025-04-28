from django.urls import path
from .views import *

urlpatterns = [
    path('main/', Main.as_view(), name='main'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateAPIView.as_view(), name='profile_update'),
    path('profile/delete/', ProfileDeleteAPIView.as_view(), name='profile_delete'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth_one/', AuthOne.as_view(), name='auth_one'),
    path('auth_two/', AuthTwo.as_view(), name='auth_two'),
]