from django.shortcuts import render
from django.http import HttpResponse
from  .models import *


def app(request):
    products = Product.objects.all()
    context = { 'products': products}
    return render(request, 'app/app.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}

    context = { 'items': items, 'cart': cart}
    return render(request, 'app/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}

    context = { 'items': items, 'cart': cart}
    return render(request, 'app/checkout.html', context)