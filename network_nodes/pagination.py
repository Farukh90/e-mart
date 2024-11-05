from rest_framework.pagination import PageNumberPagination


class MyPaginator(PageNumberPagination):
    """
    page_size (int): Количество объектов на одной странице по умолчанию (5).
    page_query_param (str): Параметр запроса для указания номера страницы ("page").
    max_page_size (int): Максимально допустимый размер страницы (20).
    """

    page_size = 5
    page_query_param = "page"
    max_page_size = 20
