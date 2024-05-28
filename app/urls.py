from django.urls import path
from . import views

urlpatterns = [
    path('', views.app, name='app'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
]

