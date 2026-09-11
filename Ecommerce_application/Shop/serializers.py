from rest_framework import serializers
from .models import Store, Product, Review


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'description',
            'store',
        ]


class StoreSerializer(serializers.ModelSerializer):

    class Meta:

        model = Store

        fields = [
            'id',
            'name',
            'description',
            'vendor',
        ]

        read_only_fields = [
            'vendor',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'product',
            'user',
            'rating',
            'comment',
            'verified',
        ]
        read_only_fields = [
            'user',
            'verified',
        ]