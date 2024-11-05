from django.contrib import admin

from .models import NetworkNode, Product


class NetworkNodeAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели NetworkNode, отображающая список узлов сети
    с возможностью фильтрации и поиска. Также добавлено действие для очистки задолженности.
    """

    list_display = ("name", "country", "city", "supplier", "debt", "created_at")
    list_filter = ("city",)
    search_fields = ("name",)
    search_help_text = "Поиск по названию"

    # Действие для очистки задолженности
    actions = ["clear_debt"]

    def clear_debt(self, request, queryset):
        """
        Админ-действие для сброса задолженности на 0 для выбранных объектов.

        Параметры:
        - request: запрос от администратора.
        - queryset: набор объектов, к которым применяется действие.
        """
        queryset.update(debt=0)

    clear_debt.short_description = "Очистить задолженность перед поставщиком"


class ProductsAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Product, отображающая список продуктов с возможностью
    фильтрации по поставщику и поиска по названию.
    """

    list_display = (
        "name",
        "model",
        "release_date",
        "supplier",
    )
    list_filter = ("supplier",)
    search_fields = ("name",)
    search_help_text = "Поиск по названию"


admin.site.register(NetworkNode, NetworkNodeAdmin)
admin.site.register(Product, ProductsAdmin)
