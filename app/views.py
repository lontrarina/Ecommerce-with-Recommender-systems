from django.shortcuts import render
from django.http import HttpResponse

def all_users(request):
    return HttpResponse("Return all users!")
# Create your views here.

def app(request):
    context = {}
    return render(request, 'app/app.html', context)


def cart(request):
    context = {}
    return render(request, 'app/cart.html', context)

def checkout(request):
    context = {}
    return render(request, 'app/checkout.html', context)