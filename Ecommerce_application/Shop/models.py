from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    '''Model representing a store created by a Vendor
    
    Fields:
    - ID: Unique integer used to identify the store.
    - Store Name: Unique string used to identify the store.
    - Description: Unique description of the store.
    - Vendor: The username of the vendor who created the store.
    '''

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)

class Product(models.Model):
    '''
    Model representing a product available for sale.

    Fields:
    - ID: Unique integer used for the system to identify the product.
    - Product Name: Unique String used for users to identify the product.
    - Price: Price of the product
    - Description: Unique description of the prodict. 
    - Store: The store to which the product belongs.
    '''

    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(max_length=100)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True
    )


class Cart(models.Model):
    '''
    Model representing a user's cart.
    '''

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class CartItem(models.Model):
    '''
    Model representing an item within a user's cart.
    '''

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    '''
    Model representing a completed order.
    '''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)

class OrderItem(models.Model):
    '''
    Model representing a product purchased in an order.
    '''

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Review(models.Model):
    '''
    Model representing a review left by a user for a product.
    '''

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    verified = models.BooleanField(default=False)