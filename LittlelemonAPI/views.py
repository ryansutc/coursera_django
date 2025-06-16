from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User, Group

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, MenuItem
from .serializers import MenuItemSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework import generics, viewsets, status

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .throttles import TenCallsPerMinute

from django.core.paginator import Paginator, EmptyPage

# class MenuItemsView(generics.ListCreateAPIView):
#     # make getting related data more efficient!!!
#     items = MenuItem.objects.select_related("category").all()
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer


@api_view(["GET", "POST"])
def menu_items(request):

    # Only allow POST method for admin users
    if request.method != "GET" and not request.user.is_staff:
        return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

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


# class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer


class CategoriesView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        """
        Allow any user to view categories, but only admin users can modify them.
        """
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]


# @api_view()
# def category_detail(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     serialized_category = CategorySerializer(category)
#     return Response(serialized_category.data)


# @api_view()
# def single_item(request, id):
#     item = get_object_or_404(MenuItem, pk=id)
#     serialized_item = MenuItemSerializer(item)
#     return Response(serialized_item.data)


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response(
        {"message": "This is a throttled endpoint for users!"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "GET"])
@permission_classes([IsAdminUser])
def managers(request):
    """
    view managers or
    Add a user to the staff or admin group
    """
    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST
        )
    elif request.method == "POST":
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="manager")
        user.groups.add(group)
        user.save()
    elif request.method == "DELETE":
        managers.user_set.remove(user)
    else:
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    return Response({"message": "ok"})
