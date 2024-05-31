from django.shortcuts import render
from django.http import JsonResponse
import json 
from  .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils import get_similar_products

def app(request):
    customer=None
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
    context = { 'products': products, 'cartItems': cartItems, 'customer':customer}
    return render(request, 'app/app.html', context)


def cart(request):
    customer=None
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items
        message=""
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']
        message="Please login to use cart"

    context = { 'items': items, 'cart': cart, 'cartItems': cartItems, 'customer':customer, 'message':message}
    return render(request, 'app/cart.html', context)

def checkout(request):
    customer=None
    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    context = { 'items': items, 'cart': cart, 'cartItems': cartItems, 'customer':customer}
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


# PRODUCT PAGE----------------------------------------------------------------------------------------------------

def product_detail(request, id):
    customer=None
    product = get_object_or_404(Product, id=id)
    related_products = get_similar_products(product)

    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        all_products = Product.objects.all()
        cartItems= cart.get_cart_items
    else:
        all_products = Product.objects.all()
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    context = {
        'product': product,
        'all_products': all_products,
        'related_products': related_products,
        'cartItems': cartItems,
        'customer':customer
    }
    return render(request, 'app/product_detail.html', context)

# AUTHORIZATION----------------------------------------------------------------------------------------------------

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('app')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username, email=user.email)
            login(request, user)
            return redirect('app')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('app')



# WISHLIST----------------------------------------------------------------------------------------------------
def wishlist(request):
    wishlist = None
    customer=None
    if request.user.is_authenticated:
        customer = request.user.customer
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        items = wishlist.wishlistitem_set.all()
        message=""
    else:
        items = []
        message="Please login to use wishlist"

    context = { 'items': items, 'wishlist': wishlist, 'customer':customer, 'message':message}
    return render(request, 'app/wishlist.html', context)


def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id)
    if request.method == "POST":
        item.delete()
        return redirect('wishlist')
    

@csrf_exempt
def update_wishlist(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(customer=customer)

    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    wishlist_item.save()

    return JsonResponse('Item was added', safe=False)
