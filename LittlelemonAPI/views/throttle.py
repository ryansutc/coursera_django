from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def throttle_check_auth(request):
    """
    This is just for testing throttling.
    """
    return Response(
        {"message": "This is a throttled endpoint for users!"},
        status=200,
    )
