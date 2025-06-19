from rest_framework import serializers
from .models import Category, MenuItem, CartItem, Order
from decimal import Decimal
import bleach
from typing import Any, Dict

from django.db import IntegrityError


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]

    def validate_slug(self, value: str) -> str:
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

    def validate_title(self, value: str) -> str:
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
            "featured",
        ]

    def calculate_tax(self, product: MenuItem) -> str:
        # for financial calculations, float cannot be relied upon. floating-point. 0.2
        price = product.price * Decimal(1.1)
        return f"{price:.2f}"

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if "price" in attrs and attrs["price"] < 2:
            raise serializers.ValidationError("Price should not be less than 2.0")
        if "inventory" in attrs and attrs["inventory"] < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return super().validate(attrs)

    def update(self, instance: MenuItem, validated_data: Dict[str, Any]) -> MenuItem:
        # update the category_id field
        category_id = validated_data.pop("category_id", None)
        if category_id is not None:
            from .models import Category

            instance.category = Category.objects.get(id=category_id)
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "menuitem", "quantity"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if "quantity" not in attrs:
            raise serializers.ValidationError("Quantity is required.")

        if attrs["quantity"] < 0:
            attrs["quantity"] = 0
        attrs["user_id"] = self.context["request"].user.id
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> CartItem:
        # Attach the user from context
        validated_data["user_id"] = self.context["request"].user.id
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "This menu item is already in your cart."}
            )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "total", "date"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        usergroup = self.context["user"].groups

        if (
            not usergroup.filter(name="manager").exists()
            and not usergroup.filter(name="delivery").exists()
        ):
            raise serializers.ValidationError("User is not a manager or delivery crew.")

        if self.instance and self.context["request"].method == "PATCH":
            # Only allow delivery_crew to be updated
            if self.context["user"].groups.filter(name="manager").exists():
                if set(attrs.keys()) - {"delivery_crew"}:
                    raise serializers.ValidationError(
                        "Only delivery_crew can be updated."
                    )
                return super().validate(attrs)
            elif self.context["user"].groups.filter(name="delivery").exists():
                if set(attrs.keys()) - {"status"}:
                    raise serializers.ValidationError("Only status can be updated.")
                return super().validate(attrs)
        return super().validate(attrs)
