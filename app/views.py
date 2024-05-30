from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json 
from  .models import *


def app(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    products = Product.objects.all()
    context = { 'products': products, 'cartItems': cartItems}
    return render(request, 'app/app.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    context = { 'items': items, 'cart': cart, 'cartItems': cartItems}
    return render(request, 'app/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    context = { 'items': items, 'cart': cart, 'cartItems': cartItems}
    return render(request, 'app/checkout.html', context)


def updateItem(request):
    data= json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    cart, created = Cart.objects.get_or_create(customer=customer)

    cartItem, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if action == 'add':
        cartItem.quantity = (cartItem.quantity + 1)
    elif action == 'remove':
        cartItem.quantity = (cartItem.quantity - 1)

    cartItem.save()

    if cartItem.quantity <= 0:
        cartItem.delete()


    return JsonResponse('Item was added', safe=False)