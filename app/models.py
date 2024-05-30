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
    
    
class InteractionHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #return f"Customer: {self.customer.name}, Product: {self.product.name}"
        return str(self.id)
    


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.id)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.id)
    
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.id)