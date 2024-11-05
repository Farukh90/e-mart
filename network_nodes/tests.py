from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import NetworkNode

User = get_user_model()


class BaseTestSetup(APITestCase):
    """
    Базовый класс для настройки тестов, включающий вспомогательные методы
    для создания пользователей и узлов сети.
    """

    def create_user(self, email, password, is_active=True):
        """
        Создает и возвращает пользователя с заданными email, паролем и статусом активности.

        Параметры:
            email (str): Электронная почта пользователя.
            password (str): Пароль пользователя.
            is_active (bool): Флаг активности пользователя (по умолчанию True).

        Возвращает:
            User: Созданный пользователь.
        """
        user = User(email=email, is_active=is_active)
        user.set_password(password)
        user.save()
        return user

    def create_network_node(self, **kwargs):
        """
        Создает и возвращает узел сети (NetworkNode) с указанными параметрами.

        Параметры:
            **kwargs: Переопределяемые значения полей модели NetworkNode.

        Возвращает:
            NetworkNode: Созданный узел сети.
        """
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

    def setUp(self):
        """
        Настраивает тестовые данные, создавая активного и неактивного пользователя,
        а также поставщика узлов сети.
        """
        self.active_user = self.create_user(
            "active@example.com", "password", is_active=True
        )
        self.inactive_user = self.create_user(
            "inactive@example.com", "password", is_active=False
        )
        self.supplier = self.create_network_node(name="Supplier Node")
        self.client.force_authenticate(user=self.active_user)

    def test_create_network_node(self):
        """
        Тестирует создание нового узла сети с заданными данными и проверяет,
        что он создается успешно с ожидаемыми значениями.
        """
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

    def test_filter_network_node_by_country(self):
        """Тест на фильтрацию NetworkNode по стране"""
        # Создаем узел NetworkNode с конкретной страной для фильтрации
        self.create_network_node(name="Node in USA", country="USA")

        url = reverse("networknode-list") + "?country=USA"
        response = self.client.get(url)

        # Проверяем, что результат содержит только один узел с указанной страной
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["country"], "USA")

    def test_update_network_node_debt_denied(self):
        """
        Тестирует запрет на обновление поля 'debt' в узле сети.
        """
        url = reverse("networknode-detail", args=[self.supplier.id])
        data = {"name": "Updated Supplier Node", "debt": 200.00}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debt", response.data)

    def test_access_denied_for_inactive_user(self):
        """
        Тестирует, что неактивному пользователю отказано в доступе к API для узлов сети.
        """
        self.client.force_authenticate(user=self.inactive_user)
        url = reverse("networknode-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductTests(BaseTestSetup):
    """
    Тесты для модели Product, включая создание продуктов.
    """

    def setUp(self):
        """
        Настраивает тестовые данные, создавая активного пользователя
        и поставщика для продуктов.
        """
        self.user = self.create_user("user@example.com", "password", is_active=True)
        self.supplier = self.create_network_node(name="Supplier Node")
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        """
        Тестирует создание нового продукта и проверяет, что он создается успешно
        с ожидаемыми значениями.
        """
        url = reverse("product-list")
        data = {
            "name": "Product A",
            "model": "Model X",
            "release_date": "2024-01-01",
            "supplier": self.supplier.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Product A")


class NetworkNodeHierarchyTests(BaseTestSetup):
    """
    Тесты для проверки иерархии узлов сети.
    """

    def setUp(self):
        """
        Создает иерархию узлов сети из трех уровней.
        """
        self.factory = self.create_network_node(
            name="Factory Node", type=NetworkNode.FACTORY
        )
        self.retail = self.create_network_node(
            name="Retail Node", type=NetworkNode.RETAIL, supplier=self.factory
        )
        self.entrepreneur = self.create_network_node(
            name="Entrepreneur Node",
            type=NetworkNode.ENTREPRENEUR,
            supplier=self.retail,
        )

    def test_hierarchy_levels(self):
        """
        Проверяет правильность вычисления уровней иерархии для каждого узла.
        """
        self.assertEqual(self.factory.get_hierarchy_level(), 0)
        self.assertEqual(self.retail.get_hierarchy_level(), 1)
        self.assertEqual(self.entrepreneur.get_hierarchy_level(), 2)

    def test_str_representation(self):
        """
        Проверяет строковое представление каждого узла в иерархии.
        """
        self.assertEqual(str(self.factory), "Factory Node (Завод, Уровень: 0)")
        self.assertEqual(str(self.retail), "Retail Node (Розничная сеть, Уровень: 1)")
        self.assertEqual(
            str(self.entrepreneur),
            "Entrepreneur Node (Индивидуальный предприниматель, Уровень: 2)",
        )
