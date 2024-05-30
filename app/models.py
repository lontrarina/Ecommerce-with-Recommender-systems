from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=False)
    email = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.CharField(max_length=50)
    season= models.CharField(max_length=50)
    styles= models.CharField(max_length=70) # boho\classic\sporty\casual
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    
class InteractionHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.customer.name}, Product: {self.product.name}"
    


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Cart owner: {self.customer.name}"
    
    @property
    def get_cart_total(self): 
        cartitems = self.cartitem_set.all()
        total = sum([item.get_total for item in cartitems])
        return total
    
    @property
    def get_cart_items(self):
        cartitems = self.cartitem_set.all()
        total = sum([item.quantity for item in cartitems])
        return total
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart owner: {self.cart.customer.name}, Product: {self.product.name}"
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Wishlist owner: {self.customer.name}"
    
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"WWishlist owner: {self.wishlist.customer.name}, Product: {self.product.name}"