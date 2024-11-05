from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserCreateAPIViewTests(APITestCase):
    def test_create_user(self):
        """Тест на создание нового пользователя"""
        url = reverse(
            "users:register"
        )  # Предположим, что этот URL соответствует UserCreateAPIView
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
        }
        response = self.client.post(url, data, format="json")

        # Проверяем, что пользователь создан успешно
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что пользователь действительно существует в базе данных
        user = User.objects.get(email="newuser@example.com")
        self.assertIsNotNone(user)

        # Проверяем, что пароль был сохранен в зашифрованном виде
        self.assertNotEqual(
            user.password, data["password"]
        )  # Пароль не должен храниться в открытом виде
        self.assertTrue(
            user.check_password(data["password"])
        )  # Пароль должен быть корректно зашифрован
