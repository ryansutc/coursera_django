from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from rest_framework.validators import UniqueValidator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


# Create your models here.
class MenuItem(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(2)], db_index=True
    )  # total price = unit price * quantity
    inventory = models.SmallIntegerField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
    featured = models.BooleanField(default=False, db_index=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
    )
    quantity = (models.SmallIntegerField(),)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("menuitem", "user")


class Order(models.Model):
    """
    when a user presses checkout on a cart w. items,
    the cart disappears and becomes an order.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="delivery_crew",  # b/c we have 2 fields that use FK for user!
    )
    status = models.BooleanField(db_index=True, default=0)  # is order delivered?
    total = models.DecimalField(max_digits=6, decimal_places=2)  # price of all items!
    date = models.DateField(db_index=True)  # when order placed


class OrderItem(models.Model):
    """
    After order is placed, cart items become order items.
    """

    order = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    # tutorial reqires unit_price and price here.
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(
        max_digits=6, decimal_places=2
    )  # total price = unit price * quantity

    class Meta:
        unique_together = ("order", "menuitem")
