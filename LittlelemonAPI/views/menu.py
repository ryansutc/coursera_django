from LittlelemonAPI.views import *
from LittlelemonAPI.serializers import MenuItemSerializer, CheckoutResponseSerializer
from LittlelemonAPI.models import MenuItem, Category
from LittlelemonAPI.permissions import IsManagerUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@extend_schema(
    methods=["GET", "POST"],
    request=MenuItemSerializer,
    responses={200: MenuItemSerializer(many=True), 201: MenuItemSerializer},
    description="List or create menu items. POST is manager-only.",
    tags=["Menu Items"],
)
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

@extend_schema(
    methods=["GET", "PUT", "PATCH", "DELETE"],
    request=MenuItemSerializer,
    responses={200: MenuItemSerializer},
    description="view or modify a single menu item.",
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def single_item(request, pk):
    # Only admin/staff users can use non-GET methods
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

@extend_schema(
    methods=["GET", "POST"],
    request=MenuItemSerializer,
    responses={
        200: MenuItemSerializer,
        404: OpenApiResponse(description="No special item for today."),
        403: OpenApiResponse(description="Admin only."),
        400: OpenApiResponse(description="Item ID is required."),
    },
    description="view/update featured menu item.",
)
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
