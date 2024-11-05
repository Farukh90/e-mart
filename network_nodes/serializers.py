from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import NetworkNode, Product


class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Позволяет конвертировать объекты узлов сети
    в формат JSON и обратно.

    Особенности:
        - Поле "debt" защищено от обновления. При попытке обновления этого поля
          выбрасывается ошибка валидации.
    """

    class Meta:
        model = NetworkNode
        fields = "__all__"

    def update(self, instance, validated_data):
        if "debt" in validated_data:
            raise ValidationError({"debt": "Обновление поля 'debt' запрещено."})

        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "model", "release_date", "supplier"]
