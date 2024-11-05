from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import NetworkNode, Product
from .pagination import MyPaginator
from .permissions import IsActiveEmployee
from .serializers import NetworkNodeSerializer, ProductSerializer


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    - Только активные сотрудники могут использовать API (IsActiveEmployee).
    - Фильтрация по стране с помощью параметра запроса "country".
    - Используется кастомный пагинатор MyPaginator для ограничения результатов на странице.
    """

    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country"]
    pagination_class = MyPaginator


class ProductViewSet(viewsets.ModelViewSet):
    """
    - Только активные сотрудники могут использовать API (IsActiveEmployee).
    - Используется кастомный пагинатор MyPaginator для управления размером страниц.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
    pagination_class = MyPaginator
