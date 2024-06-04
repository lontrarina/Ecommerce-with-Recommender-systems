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
from .utils import *
from fuzzywuzzy import process



def app(request):
    customer=None
    Is_history = False
    recommendations_NMF = []
    if request.user.is_authenticated:
        customer = request.user.customer
        target_customer_id = customer.id
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cartItems= cart.get_cart_items

        TARGET_interaction_history = InteractionHistory.objects.filter(customer=customer)
        Is_history = TARGET_interaction_history.exists()

        if Is_history:
            customers = Customer.objects.all()
            products = Product.objects.all()
            all_interaction_history = InteractionHistory.objects.all()
            recommendations_NMF= get_recommendations_NMF(target_customer_id, customers,products, all_interaction_history )
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    products = Product.objects.all()
    context = { 'products': products, 'cartItems': cartItems, 'customer':customer, 'recommendations_NMF':recommendations_NMF, 'Is_history': Is_history}
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
    all_interaction_history = InteractionHistory.objects.all()


    similar_products_content = get_similar_products_content_based(product)
    similar_products_tfidf = get_similar_produc_tfidf(product)
    similar_products_collaborative=get_recommendations_collaborative_item_item(product, all_interaction_history, Customer.objects.all(), Product.objects.all())


    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        all_products = Product.objects.all()
        cartItems= cart.get_cart_items
      #  InteractionHistory.objects.create(customer=customer, product=product)
        InteractionHistory.objects.get_or_create(customer=customer, product=product)
    else:
        all_products = Product.objects.all()
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems= cart['get_cart_items']

    context = {
        'product': product,
        'all_products': all_products,
        'related_products': similar_products_content,
        'related_products_tfidf': similar_products_tfidf,
        'related_products_collaborative': similar_products_collaborative,
        'cartItems': cartItems,
        'customer':customer
    }
    return render(request, 'app/product_detail.html', context)

# AUTHORIZATION----------------------------------------------------------------------------------------------------

def login_view(request):
    cart = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = cart['get_cart_items']

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
    return render(request, 'app/login.html', {'form': form, 'cartItems': cartItems})

def register_view(request):
    cart = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = cart['get_cart_items']
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username, email=user.email)
            login(request, user)
            return redirect('app')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form, 'cartItems': cartItems})

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
        cart, created = Cart.objects.get_or_create(customer=customer)
        cartItems = cart.get_cart_items
        message=""
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = cart['get_cart_items']
        message="Please login to use wishlist"

    context = { 'items': items, 'wishlist': wishlist, 'customer':customer, 'message':message, 'cartItems': cartItems,}
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

# SEARCH----------------------------------------------------------------------------------------------------
def search(request):
    customer=None
    query = request.GET.get('q')
    products_results = []

    if request.user.is_authenticated:
        customer = request.user.customer
        cart, created = Cart.objects.get_or_create(customer=customer)
        cartItems = cart.get_cart_items
    else:
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = cart['get_cart_items']

    if query:
        products = Product.objects.all()
        product_names = [product.name for product in products]
        results = process.extract(query, product_names, limit=10)
        
        # Встановлюємо вищий поріг для фільтрації слабких збігів
        threshold = 70
        matched_product_ids = []
        
        for result in results:
            if result[1] >= threshold:
                matched_product = Product.objects.filter(name__icontains=result[0]).first()
                if matched_product:
                    matched_product_ids.append(matched_product.id)
        
        products_results = Product.objects.filter(id__in=matched_product_ids)
    else:
        products_results = Product.objects.all()

    context = {
        'products_results': products_results,
        'cartItems': cartItems,
        'customer':customer
    }

    return render(request, 'app/search_results.html', context)


# INTERACTION HISTORY----------------------------------------------------------------------------------------------------

def view_history(request):
   # wishlist = None
    customer=None

    if request.user.is_authenticated:
        customer = request.user.customer
        interaction_history = InteractionHistory.objects.filter(customer=customer)
        cart, created = Cart.objects.get_or_create(customer=customer)
        cartItems = cart.get_cart_items
        message=""
    else:
        items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = cart['get_cart_items']
        message="Please login to use wishlist"

    context = { 'customer':customer, 'message':message, 'cartItems': cartItems, 'interaction_history_items': interaction_history}
    return render(request, 'app/interaction_history.html', context)


def remove_from_history(request, item_id):
    item = get_object_or_404(InteractionHistory, id=item_id)
    if request.method == "POST":
        item.delete()
        return redirect('view_history')
