from django.db import models

# Create your models here.


# class Book(models.Model):
#     title = models.CharField(max_length=200)
#     author = models.CharField(max_length=100)
#     publication_date = models.DateField()

#     def __str__(self):
#         return self.title

# class Users(models.Model):
#     name = models.CharField(max_length=200)
#     email = models.CharField(max_length=100)
#     password = models.CharField(max_length=100)
#     phone = models.CharField(max_length=100)
#     address = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name
    
# class Products(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.CharField(max_length=100)
#     price = models.CharField(max_length=100)
#     image = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name
    
# class Orders(models.Model):
#     user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
#     product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
#     quantity = models.CharField(max_length=100)
#     total_price = models.CharField(max_length=100)
#     order_date = models.DateField()

