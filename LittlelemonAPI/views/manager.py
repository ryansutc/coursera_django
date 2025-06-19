from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from drf_spectacular.utils import extend_schema, OpenApiResponse
from LittlelemonAPI.permissions import IsManagerUser

@extend_schema(
    methods=["POST", "GET"],
    request=None,
    responses={
        200: OpenApiResponse(description="List of managers or success message."),
        400: OpenApiResponse(description="Username is required."),
        403: OpenApiResponse(description="Only staff users can add/delete managers."),
        405: OpenApiResponse(description="Method not allowed."),
    },
)
@api_view(["POST", "GET"])
@permission_classes([IsManagerUser])
def managers(request):
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
            {"error": "Username is required."}, status=400
        )
    elif request.method == "POST":
        if not request.user.is_staff:
            return Response(
                {"error": "Only 'staff' users can add managers."},
                status=403,
            )
        user = User.objects.get(username=username)
        group = Group.objects.get(name="manager")
        user.groups.add(group)
        user.save()
    elif request.method == "DELETE":
        if not request.user.is_staff:
            return Response(
                {"error": "Only 'staff' users can delete managers."},
                status=403,
            )
        managers.user_set.remove(user)
    else:
        return Response(
            {"error": "Method not allowed."}, status=405
        )
    return Response({"message": "ok"})
