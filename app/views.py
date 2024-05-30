from django.shortcuts import render
from django.http import HttpResponse
from  .models import *


def app(request):
    products = Product.objects.all()
    context = { 'products': products}
    return render(request, 'app/app.html', context)


def cart(request):
    context = {}
    return render(request, 'app/cart.html', context)

def checkout(request):
    context = {}
    return render(request, 'app/checkout.html', context)