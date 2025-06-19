from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group

from LittlelemonAPI.models import CartItem, Category, MenuItem, Order

from rest_framework import status


class APITestSetupMixin:
    def setUp(self):
        # Create groups
        self.manager_group, _ = Group.objects.get_or_create(name="manager")
        self.delivery_group, _ = Group.objects.get_or_create(name="delivery")
        # Create users
        self.admin = User.objects.create_superuser("admin", "admin@test.com", "pass")
        self.manager = User.objects.create_user("manager", password="pass")
        self.manager.groups.add(self.manager_group)
        self.delivery = User.objects.create_user("delivery", password="pass")
        self.delivery.groups.add(self.delivery_group)
        self.user = User.objects.create_user("user", password="pass")
        # Create category and menu item
        self.category = Category.objects.create(title="Cat", slug="cat")
        self.menu_item = MenuItem.objects.create(
            title="Pizza",
            price=12.5,
            inventory=10,
            category=self.category,
            featured=True,
        )


class TestMenuItemsEndpoints(APITestSetupMixin, APITestCase):

    def test_get_menu_item_detail_url(self):
        """
        Test that the order detail URL is constructed correctly.
        """
        response = self.client.get(reverse("menu-item-detail", kwargs={"pk": self.menu_item.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.menu_item.title)

    def test_menu_items_list(self):
        url = reverse("menu-item-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) >= 1)


    def test_menu_items_post_manager_only(self):
        url = reverse("menu-item-list")
        data = {
            "title": "Burger",
            "price": 9,
            "inventory": 5,
            "category_id": self.category.id, #important: use category_id, not category!
        }
        # Unauthenticated
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Authenticated non-admin
        self.client.force_authenticate(self.user)
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Admin
        self.client.force_authenticate(self.manager)
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)

    def test_single_item_get(self):
        url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], self.menu_item.title)

    def test_single_item_edit_delete_admin_only(self):
        url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

        # PATCH as non-admin
        self.client.force_authenticate(self.user)
        resp = self.client.patch(url, {"title": "Nope"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # PATCH as admin
        self.client.force_authenticate(self.admin)
        resp = self.client.patch(url, {"title": "Updated"})
        self.assertEqual(resp.status_code, 200)
        # DELETE as non-admin
        self.client.force_authenticate(self.user)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # DELETE as admin
        self.client.force_authenticate(self.admin)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_menu_item_featured(self):
        url = reverse("featured")
        # GET featured
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # POST as non-admin
        self.client.force_authenticate(self.user)
        resp = self.client.post(url, {"item_id": self.menu_item.id})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # POST as admin
        self.client.force_authenticate(self.admin)
        resp = self.client.post(url, {"item_id": self.menu_item.id})
        self.assertEqual(resp.status_code, 200)


class TestCategoriesEndpoints(APITestSetupMixin, APITestCase):
    """
    All sorts of tests for the categories endpoints
    """
    
        
    def test_anyone_can_view_categories(self):
        """
        Test that anyone can view the categories list.
        """
        response = self.client.get(reverse("categories-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_only_manager_can_add_category(self):
        """
        to update the '/categories' as a POST request,
        you need to be logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test that a manager CAN add a category
        # self.client.login(username="test_manager", password="testpass")
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"title": "New Category", "slug": "newcategory"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_manager_can_delete_category(self):
        """
        to delete the '/categories' as a DELETE request,
        you need to be logged in.
        """
        category = Category.objects.create(title="TestCat2", slug="testcat2")
        category.save()
        
        id = category.id
        url = reverse("categories-detail", kwargs={"pk": id})
        
        # user cannot delete 
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # manager CAN delete a category
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_only_manager_can_add_category(self):
        url = reverse("categories-list")
        data = {"title": "NewCat", "slug": "newcat"}
        # Unauthenticated : will get a 401
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        # Non-manager
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Manager
        self.client.force_authenticate(user=self.manager)
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)



class TestCartAndOrderEndpoints(APITestSetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.cart_url = reverse("cart-items-list")
        self.checkout_url = reverse("checkout")
        self.order_url = reverse("order-list")
        self.cart_item = CartItem.objects.create(
            user=self.user, menuitem=self.menu_item, quantity=2
        )

    def test_cart_items_requires_auth(self):
        resp = self.client.get(self.cart_url)
        self.assertEqual(resp.status_code, 401)
        self.client.force_authenticate(self.user)
        resp = self.client.get(self.cart_url)
        self.assertEqual(resp.status_code, 200)

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(self.checkout_url)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_order_view_permissions(self):
        # Create order for user and delivery
        order = Order.objects.create(
            user=self.user, total=10, date="2024-01-01", delivery_crew=self.delivery
        )
        # User sees own order
        self.client.force_authenticate(self.user)
        resp = self.client.get(self.order_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(o["id"] == order.id for o in resp.data))
        # Delivery sees assigned order
        self.client.force_authenticate(self.delivery)
        resp = self.client.get(self.order_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(o["id"] == order.id for o in resp.data))
        # Manager sees all
        self.client.force_authenticate(self.manager)
        resp = self.client.get(self.order_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(o["id"] == order.id for o in resp.data))

    def test_order_detail_permissions(self):
        order = Order.objects.create(
            user=self.user, total=10, date="2024-01-01", delivery_crew=self.delivery
        )
        url = reverse("order-detail", kwargs={"pk": order.id})
        # User can GET own order by the id
        self.client.force_authenticate(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        # delivery crew can update order status only
        self.client.force_authenticate(self.delivery)
        resp = self.client.patch(url, {"status": 1})
        self.assertEqual(resp.status_code, 200)
        
        # User cannot DELETE
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Manager can DELETE
        self.client.force_authenticate(self.manager)
        resp = self.client.delete(url)
        self.assertIn(
            resp.status_code, [status.HTTP_204_NO_CONTENT, 404]
        )  # status.HTTP_204_NO_CONTENT if deleted, 404 if already deleted
        
        


class TestManagerGroupEndpoint(APITestSetupMixin, APITestCase):
    def test_manager_group_add_and_list(self):
        url = reverse("managers")
        # Only manager can see all managers
        self.client.force_authenticate(self.manager)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        # Only staff users can POST to make a new manager
        newmanager = User.objects.create_user("newmanager", password="pass")
        newmanager.groups.add(self.manager_group)
        newmanager.is_staff = True
        newmanager.save()
       
        #make myself a manager!@
        self.client.force_authenticate(newmanager)
        resp = self.client.post(url, {"username": newmanager.username})
        self.assertEqual(resp.status_code, 200)
        
        # even manager forbidden
        self.client.force_authenticate(self.manager)
        resp = self.client.post(url, {"username": newmanager.username})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
