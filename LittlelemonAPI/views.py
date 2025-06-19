import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

# Create your views here.
from rest_framework.response import Response

from .permissions import IsManagerUser
from .utils import get_best_delivery_person
from .models import Category, MenuItem, CartItem, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    CartItemSerializer,
    OrderSerializer,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework import viewsets, status

from rest_framework.permissions import IsAuthenticated, AllowAny
from .throttles import TenCallsPerMinute

from django.core.paginator import Paginator, EmptyPage

# class MenuItemsView(generics.ListCreateAPIView):
#     # make getting related data more efficient!!!
#     items = MenuItem.objects.select_related("category").all()
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer


@api_view(["GET", "POST"])
def menu_items(request):

    # Only allow POST method for manager users
    user = request.user
    if request.method != "GET" and not user.groups.filter(name="manager").exists(): 
        return Response({"detail": "managers only."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(page)
        except EmptyPage:
            items = []
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data)

    elif request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def single_item(request, pk):

    # Only allow non-GET methods for admin users
    if request.method != "GET" and not request.user.is_staff:
        return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        item = get_object_or_404(MenuItem, pk=pk)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    elif request.method == "PUT":
        item = get_object_or_404(MenuItem, pk=pk)
        serialized_item = MenuItemSerializer(item, data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data)
    elif request.method == "PATCH":
        item = get_object_or_404(MenuItem, pk=pk)
        serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data)
    elif request.method == "DELETE":
        item = get_object_or_404(MenuItem, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def menu_item_featured(request):
    """
    View to get the menu item of the day or
    to set it via POST.
    """

    if request.method == "GET":
        try:
            item = MenuItem.objects.get(featured=True)
            serialized_item = MenuItemSerializer(item)
            return Response(serialized_item.data)
        except MenuItem.DoesNotExist:
            return Response(
                {"detail": "No special item for today."},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif request.method == "POST":
        if not request.user.is_staff:
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        item_id = request.data.get("item_id")
        if not item_id:
            return Response(
                {"detail": "Item ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            item = MenuItem.objects.get(pk=item_id)
            MenuItem.objects.update(featured=False)  # reset previous featured item
            item.featured = True
            item.save()
            serialized_item = MenuItemSerializer(item)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response(
                {"detail": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND
            )


class CategoriesView(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
        Allow any user to view categories, but only admin users can modify them.
        """
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsManagerUser()]
        return [AllowAny()]  # Allow anyone to view categories


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    """
    This is just for testing throttling.
    """
    return Response(
        {"message": "This is a throttled endpoint for users!"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "GET"])
@permission_classes([IsManagerUser])
def managers(request):
    """
    view users who are managers (GET) or
    Add a user to the staff or admin group
    """

    if request.method == "GET":
        managers = Group.objects.get(name="manager")
        users = managers.user_set.all()
        serialized_users = [
            {"username": user.username, "id": user.id} for user in users
        ]
        return Response(serialized_users)

    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST
        )
    elif request.method == "POST":
        if not request.user.is_staff:
            return Response(
                {"error": "Only 'staff' users can add managers."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="manager")
        user.groups.add(group)
        user.save()
    elif request.method == "DELETE":
        if not request.user.is_staff:
            return Response(
                {"error": "Only 'staff' users can delete managers."},
                status=status.HTTP_403_FORBIDDEN,
            )
        managers.user_set.remove(user)
    else:
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    return Response({"message": "ok"})


class CartItemsView(viewsets.ModelViewSet):
    """
    View to manage the cart.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user.id)


class OrderItemsView(viewsets.ModelViewSet):
    """
    View to manage the order.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user.id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order(request):
    """
    View to see orders. Managers see all,
    users see their own orders and delivery crew
    see orders assigned to them.
    """

    user = request.user

    if request.method == "GET":
        orders = None
        if user.groups.filter(name="manager").exists():
            # Managers can see all orders
            orders = Order.objects.all()
        elif user.groups.filter(name="delivery").exists():
            # Delivery crew can see orders assigned to them
            orders = Order.objects.filter(delivery_crew=user)
        else:
            # Regular users can only see their own orders
            orders = Order.objects.filter(user=user)

        serialized_order = OrderSerializer(orders, many=True)
        return Response(serialized_order.data)
    


@api_view(["GET", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    """
    View to manage a specific order.
    Managers can edit any order, users can only view their own orders.
    """
    user = request.user

    if request.method == "GET":
        order = get_object_or_404(Order, pk=pk)
        if user.groups.filter(name="manager").exists() or order.user == user:
            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data)
        else:
            return Response(
                {"detail": "You do not have permission to view this order."},
                status=status.HTTP_403_FORBIDDEN,
            )
    elif request.method == "DELETE":
        if not user.groups.filter(name="manager").exists():
            return Response(
                {"detail": "You do not have permission to delete orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, pk=pk, user=request.user)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == "PATCH":
        if not user.groups.filter(name="manager").exists() and not user.groups.filter(name="delivery").exists():
            return Response(
                {"detail": "You do not have permission to edit orders."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, pk=pk)
        serialized_order = OrderSerializer(
            order,
            data=request.data,
            partial=True,
            context={"request": request, "user": user},
        )
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()
        return Response(
            serialized_order.data,
        )

    return Response(
        {"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    """
    View to checkout the cart items and create an order.
    """
    user = User.objects.get(id=request.user.id)
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        return Response(
            {"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
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

    # Clear the cart after checkout
    cart_items.delete()

    return Response(
        {"detail": "Order created successfully.", "order_id": order.id},
        status=status.HTTP_201_CREATED,
    )
