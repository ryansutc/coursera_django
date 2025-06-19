from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r"categories", views.CategoriesView, basename="categories")

router.register(r"cart-items", views.CartItemsView, basename="cart-items")
router.register(r"order-items", views.OrderItemsView, basename="order-items")

urlpatterns = [
    path("menu-items/", views.menu_items, name="menu-items"),
    path("menu-items/<int:pk>/", views.single_item, name="menu-item"),
    path("menu-items/featured/", views.menu_item_featured, name="featured"),
    path("cart-items/checkout/", views.checkout, name="checkout"),
    path("", include(router.urls)),
    path("", include(router.urls)),
    # path("category/<int:pk>", views.category_detail, name="category-detail"),
    path("throttle-check-auth/", views.throttle_check_auth),
    path(
        "api-token-auth/", obtain_auth_token
    ),  # django rest framework token authentication endpoint (POST)
    path("groups/manager/users/", views.managers, name="managers"),
    path("orders/", views.order, name="order"),
    path(
        "orders/<int:pk>/",
        views.order_detail,
        name="orders",
    ),
]
