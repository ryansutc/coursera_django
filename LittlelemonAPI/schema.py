import graphene
from graphene_django import DjangoObjectType, DjangoListField
from django.contrib.auth.models import User
from .models import Order, MenuItem, Category, CartItem, OrderItem
from graphene_django.debug import DjangoDebug
# https://graphql.org/learn/

# Add UserType for the User model
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'date', 'delivery_crew']
    
    order_delivery_crew = graphene.String()
    
    def resolve_order_delivery_crew(self, info):
        return self.delivery_crew.username if self.delivery_crew else "No delivery crew assigned"

class MenuItemType(DjangoObjectType):
    class Meta:
        model = MenuItem
        fields = "__all__"

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"
        
class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
        fields = "__all__"

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = "__all__"
        
class Query(graphene.ObjectType):
    orders = graphene.List(OrderType)
    menu_items = graphene.List(MenuItemType)
    categories = graphene.List(CategoryType)
    cart_items = graphene.List(CartItemType)
    order_items = graphene.List(OrderItemType)

    
    def resolve_orders(self, info):
        return Order.objects.all().select_related('delivery_crew', 'user').all()
    
    def resolve_orders_with_delivery_crew(self, info):
        return Order.objects.all().select_related('delivery_crew', 'user').all()
    
    def resolve_menu_items(self, info):
        return MenuItem.objects.all()

    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_cart_items(self, info):
        return CartItem.objects.all()

    def resolve_order_items(self, info):
        return OrderItem.objects.all()
    
    debug = graphene.Field(DjangoDebug, name='_debug')
    
schema = graphene.Schema(query=Query)