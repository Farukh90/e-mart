from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import NetworkNodeAdmin
from .models import NetworkNode

User = get_user_model()


class BaseTestSetup(APITestCase):
    """
    Базовый класс для настройки тестов, включающий вспомогательные методы
    для создания пользователей и узлов сети.
    """

    @classmethod
    def create_user(cls, email, password, is_active=True):
        user = User(email=email, is_active=is_active)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_network_node(cls, **kwargs):
        defaults = {
            "name": "Default Node",
            "email": "default@example.com",
            "country": "Default Country",
            "city": "Default City",
            "street": "Default St",
            "building_number": "1",
            "debt": 100.00,
            "type": NetworkNode.FACTORY,
        }
        defaults.update(kwargs)
        return NetworkNode.objects.create(**defaults)


class NetworkNodeTests(BaseTestSetup):
    """
    Тесты для модели NetworkNode, включая создание, фильтрацию, обновление и проверку прав доступа.
    """

    @classmethod
    def setUpTestData(cls):
        cls.active_user = cls.create_user(
            "active@example.com", "password", is_active=True
        )
        cls.inactive_user = cls.create_user(
            "inactive@example.com", "password", is_active=False
        )
        cls.supplier = cls.create_network_node(name="Supplier Node")
        cls.node1 = cls.create_network_node(
            name="Node 1", email="node1@example.com", debt=100.00
        )
        cls.node2 = cls.create_network_node(
            name="Node 2", email="node2@example.com", debt=200.00
        )

        # Экземпляр AdminSite и NetworkNodeAdmin для действий админа
        cls.site = AdminSite()
        cls.admin = NetworkNodeAdmin(NetworkNode, cls.site)

    def setUp(self):
        self.client.force_authenticate(user=self.active_user)

    def test_create_network_node(self):
        url = reverse("networknode-list")
        data = {
            "name": "Retail Node",
            "email": "retail@example.com",
            "country": "Canada",
            "city": "City B",
            "street": "Broadway",
            "building_number": "2",
            "supplier": self.supplier.id,
            "debt": 50.00,
            "type": NetworkNode.RETAIL,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["debt"], "50.00")

    def test_clear_debt_action(self):
        """
        Проверяет, что действие clear_debt устанавливает задолженность узлов в 0.
        """
        queryset = NetworkNode.objects.filter(id__in=[self.node1.id, self.node2.id])

        # Прямой вызов метода действия clear_debt, передавая None вместо request
        NetworkNodeAdmin(NetworkNode, None).clear_debt(None, queryset)

        # Обновляем объекты из базы данных и проверяем их задолженность
        self.node1.refresh_from_db()
        self.node2.refresh_from_db()
        self.assertEqual(self.node1.debt, 0)
        self.assertEqual(self.node2.debt, 0)

    def test_filter_network_node_by_country(self):
        self.create_network_node(name="Node in USA", country="USA")
        url = reverse("networknode-list") + "?country=USA"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["country"], "USA")

    def test_update_network_node_debt_denied(self):
        url = reverse("networknode-detail", args=[self.supplier.id])
        data = {"name": "Updated Supplier Node", "debt": 200.00}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debt", response.data)

    def test_access_denied_for_inactive_user(self):
        self.client.force_authenticate(user=self.inactive_user)
        url = reverse("networknode-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NetworkNodeUpdateTests(BaseTestSetup):
    """
    Тесты для проверки обновления узлов сети, включая защиту поля "debt" от обновлений.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user(
            email="testuser@example.com", password="testpassword", is_active=True
        )
        cls.node = cls.create_network_node(
            name="Test Node",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            building_number="1",
            debt=100.00,
            type=NetworkNode.FACTORY,
        )
        cls.url = reverse("networknode-detail", args=[cls.node.id])

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_update_network_node_successful(self):
        data = {"name": "Updated Node", "city": "Updated City"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка, что данные были обновлены корректно
        self.node.refresh_from_db()
        self.assertEqual(self.node.name, "Updated Node")
        self.assertEqual(self.node.city, "Updated City")
        self.assertEqual(self.node.debt, 100.00)  # Убедимся, что debt не изменился


class NetworkNodeHierarchyTests(BaseTestSetup):
    """
    Тесты для проверки иерархии узлов сети.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Создает иерархию узлов сети из трех уровней.
        """
        cls.factory = cls.create_network_node(
            name="Factory Node", type=NetworkNode.FACTORY
        )
        cls.retail = cls.create_network_node(
            name="Retail Node", type=NetworkNode.RETAIL, supplier=cls.factory
        )
        cls.entrepreneur = cls.create_network_node(
            name="Entrepreneur Node",
            type=NetworkNode.ENTREPRENEUR,
            supplier=cls.retail,
        )

    def test_hierarchy_levels(self):
        """
        Проверяет правильность вычисления уровней иерархии для каждого узла.
        """
        self.assertEqual(self.factory.get_hierarchy_level(), 0)
        self.assertEqual(self.retail.get_hierarchy_level(), 1)
        self.assertEqual(self.entrepreneur.get_hierarchy_level(), 2)
