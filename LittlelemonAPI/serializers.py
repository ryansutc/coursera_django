from rest_framework import serializers
from .models import Category, MenuItem
from decimal import Decimal
import bleach


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]

    def validate_slug(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Slug must be alphanumeric.")
        return value


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    stock = serializers.IntegerField(source="inventory", read_only=True)
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    # category = serializers.HyperlinkedRelatedField(
    #     queryset=Category.objects.all(),
    #     view_name="category-detail",
    #
    # )

    def validate_title(self, value):
        return bleach.clean(value)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "inventory",
            "stock",
            "price_after_tax",
            "category",
            "category_id",
        ]

    def calculate_tax(self, product: MenuItem):
        # for financial calculations, float cannot be relied upon. floating-point. 0.2
        price = product.price * Decimal(1.1)
        return f"{price:.2f}"
        tax_rate = 0.05

    def validate(self, attrs):
        if attrs["price"] < 2:
            raise serializers.ValidationError("Price should not be less than 2.0")
        if attrs["inventory"] < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return super().validate(attrs)
