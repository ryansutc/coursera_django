from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group

from LittlelemonAPI.models import Category, MenuItem

from rest_framework import status


class TestMenuItemsEndpoints(APITestCase):

    def setUp(self):
        """
        Steps that are run before each test method.

         -create menu-item
        """
        self.category = Category.objects.create(
            title="Test Category", slug="testcategory"
        )
        # create a new menu-item to read
        self.menu_item = MenuItem.objects.create(
            title="Test Menu Item",
            price=10.00,
            inventory=4,
            category=self.category,
            featured=True,
        )
        # benefit of named urls!
        self.url = reverse("menu-item", kwargs={"pk": 1})

    def test_get_menu_item_detail_url(self):
        """
        Test that the order detail URL is constructed correctly.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.menu_item.title)


class TestCategoriesEndpoints(APITestCase):
    """
    All sorts of tests for the categories endpoints
    """

    def setUp(self):
        """
        Steps that are run before each test method.

        - create a user in manager group

        """
        self.user = User.objects.create_user(
            username="test_manager", password="testpass"
        )
        # Ensure the "manager" group exists globally
        self.group, created = Group.objects.get_or_create(name="manager")

        # Add the user to the manager group
        self.user.groups.add(self.group)
        self.category = Category.objects.create(
            title="Test Category", slug="test-category"
        )
        # benefit of named urls!
        self.url = reverse("categories-list")

    def test_anyone_can_view_categories(self):
        """
        Test that anyone can view the categories list.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_only_manager_can_add_a_category(self):
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
        print(response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_manager_can_delete_a_category(self):
        """
        to delete the '/categories' as a DELETE request,
        you need to be logged in.
        """
        id = Category.objects.first().id
        url = reverse("categories-detail", kwargs={"pk": id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test that a manager CAN delete a category
        # self.client.login(username="test_manager", password="testpass")
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(url)
        print(response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
