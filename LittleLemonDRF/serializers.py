from rest_framework import serializers
from .models import Rating
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rating model.
    This serializer handles the creation and validation of ratings for menu items.
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Rating
        fields = ["user", "menuitem_id", "rating"]

        validators = [
            UniqueTogetherValidator(
                queryset=Rating.objects.all(), fields=["user", "menuitem_id"]
            )
        ]
        extra_kwargs = {
            "rating": {"min_value": 0, "max_value": 5},
        }
