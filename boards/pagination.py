from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    """
    Assignee : 기연

    페이지당 게시물 갯수를 지정할 수 있도록 Pagination을 구현하였습니다.
    """
    page_size_query_param = 'page_count'

