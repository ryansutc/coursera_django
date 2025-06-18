import unittest
from django.test import TestCase


class TestUtilsFunctions(unittest.TestCase):
    def test_positive_number(self):
        self.assertEqual(abs(10), 10)

    def test_negative_number(self):
        self.assertEqual(abs(-10), 10)

    def test_zero(self):
        self.assertEqual(abs(0), 0)


class TestDjangoUtilsFunctions(TestCase):
    def test_get_best_delivery_person(self):
        from LittlelemonAPI.utils import get_best_delivery_person
        from django.contrib.auth.models import User
        from unittest.mock import patch, MagicMock

        # Mock the User model and its filter method
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.groups.all.return_value = ["delivery"]

        with patch("LittlelemonAPI.utils.User.objects.filter") as mock_filter:
            mock_filter.return_value.prefetch_related.return_value = [mock_user]

            orders = [MagicMock(user=mock_user)]
            best_delivery_person = get_best_delivery_person(orders)

            self.assertEqual(best_delivery_person, mock_user)
