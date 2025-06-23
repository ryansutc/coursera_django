from django.urls import include, path

from .views import *
from rest_framework.routers import DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r"categories", CategoriesView, basename="categories")
router.register(r"cart-items", CartItemsView, basename="cart-items")
router.register(r"order-items", OrderItemsView, basename="order-items")

# make names for url patterns match the viewset name patterns as per:
# https://www.django-rest-framework.org/api-guide/routers/
# /users/ -> user-list
# /users/<int:pk>/ -> user-detail


urlpatterns = [
    path("menu-items/", menu_items, name="menu-item-list"),
    path("menu-items/<int:pk>/", single_item, name="menu-item-detail"),
    path("menu-items/featured/", menu_item_featured, name="featured"),
    path("cart-items/checkout/", checkout, name="checkout"),
    path("", include(router.urls)),
    path("", include(router.urls)),
    # path("category/<int:pk>", views.category_detail, name="category-detail"),
    path("throttle-check-auth/", throttle_check_auth),
    path(
        "api-token-auth/", obtain_auth_token
    ),  # django rest framework token authentication endpoint (POST)
    path("groups/manager/users/", managers, name="managers"),
    path("orders/", order, name="order-list"),
    path(
        "orders/<int:pk>/",
        order_detail,
        name="order-detail",
    ),
]
