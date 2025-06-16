from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Rating
from .serializers import RatingSerializer


# Create your views here.
# class RatingsView:
#     def get(self, request):
#         # Logic to handle GET request for ratings
#         return render(request, "ratings.html")

#     def post(self, request):
#         # Logic to handle POST request for ratings
#         return render(request, "ratings.html")  # Placeholder response


class RatingsView(generics.ListCreateAPIView):
    """
    View to handle listing and creating ratings.
    """

    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):

        if self.request.method in ["GET"]:
            return []
        return [IsAuthenticated()]
