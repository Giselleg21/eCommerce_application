from django import forms 
from .models import Product, Store, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Buyer', 'Buyer'),
        ('Vendor', 'Vendor'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'role'
        ]

class ProductForm(forms.ModelForm):
    '''The submitted format for products.'''
    class Meta:
        model = Product
        fields = ["name", "price", "description"]

class StoreForm(forms.ModelForm):
    '''The submitted format for Stores.'''
    class Meta:
        model = Store
        fields = ["name", "description"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

