from rest_framework import viewsets
from LittlelemonAPI.models import Category
from LittlelemonAPI.serializers import CategorySerializer
from LittlelemonAPI.permissions import IsManagerUser
from rest_framework.permissions import AllowAny

class CategoriesView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsManagerUser()]
        return [AllowAny()]
