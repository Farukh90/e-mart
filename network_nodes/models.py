from django.db import models


class NetworkNode(models.Model):
    """
    Модель, представляющая иерархический узел сети. Каждый узел может иметь поставщика, к которому
    он относится, и обладает такими атрибутами, как задолженность и контактные данные, время создания.
    """

    FACTORY = "factory"
    RETAIL = "retail"
    ENTREPRENEUR = "entrepreneur"

    NETWORK_TYPES = [
        (FACTORY, "Завод"),
        (RETAIL, "Розничная сеть"),
        (ENTREPRENEUR, "Индивидуальный предприниматель"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    email = models.EmailField(verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    building_number = models.CharField(max_length=10, verbose_name="Номер дома")
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Поставщик",
    )
    debt = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Задолженность", default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    type = models.CharField(
        max_length=15, choices=NETWORK_TYPES, verbose_name="Тип", default=RETAIL
    )

    def get_hierarchy_level(self):
        """
        Вычисляет уровень иерархии узла, проходя по цепочке поставщиков.

        Возвращает:
            int: Уровень иерархии, начиная с 0 для узлов без поставщика.
        """
        level = 0
        supplier = self.supplier
        while supplier:
            level += 1
            supplier = supplier.supplier  # Переход на следующего поставщика в цепочке
        return level

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}, Уровень: {self.get_hierarchy_level()})"

    class Meta:
        verbose_name = "Предприятие"
        verbose_name_plural = "Предприятия"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]


class Product(models.Model):
    """
    Модель продукта, который может быть привязан к поставщику из сети
    NetworkNode. Каждый продукт имеет название, модель и дату выхода на рынок.
    """

    name = models.CharField(max_length=100, verbose_name="Название")
    model = models.CharField(max_length=100, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")
    supplier = models.ForeignKey(
        NetworkNode,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Поставщик",
    )

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
