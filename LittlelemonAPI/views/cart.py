from rest_framework import viewsets
from LittlelemonAPI.models import CartItem, Order, OrderItem
from LittlelemonAPI.serializers import CartItemSerializer, CheckoutResponseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.models import User
from LittlelemonAPI.utils import get_best_delivery_person
import datetime

'''
 Items for a cart or for an order are here
'''
class CartItemsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user.id)

class OrderItemsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user.id)

@extend_schema(
    operation_id="api_checkout",
    description="View to checkout the cart items and create an order.",
    request=None,
    responses={
        201: CheckoutResponseSerializer,
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Your cart is empty."
        ),
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = User.objects.get(id=request.user.id)
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return Response(
            {"detail": "Your cart is empty."}, status=400
        )
    total_price = sum(item.menuitem.price * item.quantity for item in cart_items)
    delivery_person = get_best_delivery_person(Order.objects.all())
    order = Order.objects.create(
        user=user,
        total=total_price,
        date=datetime.date.today(),
        delivery_crew=delivery_person,
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order, menuitem=item.menuitem, quantity=item.quantity
        )
    cart_items.delete()
    return Response(
        {"detail": "Order created successfully.", "order_id": order.id},
        status=201,
    )
