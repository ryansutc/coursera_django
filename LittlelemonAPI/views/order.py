from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from LittlelemonAPI.serializers import OrderSerializer
from LittlelemonAPI.models import Order
from django.shortcuts import get_object_or_404

@extend_schema(
    operation_id="api_order_list",
    description="View to see orders. Managers see all, users see their own orders and delivery crew see orders assigned to them.",
    responses={200: OrderSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order(request):
    user = request.user
    if request.method == "GET":
        if user.groups.filter(name="manager").exists():
            orders = Order.objects.all()
        elif user.groups.filter(name="delivery").exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)
        serialized_order = OrderSerializer(orders, many=True)
        return Response(serialized_order.data)

@extend_schema(
    operation_id="api_order_details_get",
    description="Retrieve a specific order.",
    request=None,
    responses={200: OrderSerializer, 403: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Forbidden")},
    methods=["GET"]
)
@extend_schema(
    operation_id="api_order_details_patch",
    description="Update a specific order.",
    request=None,
    responses={200: OrderSerializer, 403: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Forbidden")},
    methods=["PATCH"]
)
@extend_schema(
    operation_id="api_order_details_delete",
    description="Delete a specific order.",
    request=None,
    responses={204: OpenApiResponse(description="Order deleted."), 403: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Forbidden")},
    methods=["DELETE"]
)
@api_view(["GET", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    user = request.user
    if request.method == "GET":
        order = get_object_or_404(Order, pk=pk)
        if user.groups.filter(name="manager").exists() or order.user == user:
            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data)
        else:
            return Response({"detail": "You do not have permission to view this order."}, status=403)
    elif request.method == "DELETE":
        if not user.groups.filter(name="manager").exists():
            return Response({"detail": "You do not have permission to delete orders."}, status=403)
        order = get_object_or_404(Order, pk=pk, user=request.user)
        order.delete()
        return Response(status=204)
    elif request.method == "PATCH":
        if not user.groups.filter(name="manager").exists() and not user.groups.filter(name="delivery").exists():
            return Response({"detail": "You do not have permission to edit orders."}, status=403)
        order = get_object_or_404(Order, pk=pk)
        serialized_order = OrderSerializer(
            order,
            data=request.data,
            partial=True,
            context={"request": request, "user": user},
        )
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()
        return Response(serialized_order.data)
    return Response({"detail": "Method not allowed."}, status=405)
