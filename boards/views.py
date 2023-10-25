from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from boards.filters import BoardFilter, CustomSearchFilter

from boards.models import Board
from boards.serializers import BoardListSerializer

# api/v1/boards/?query_params
class BoardsListAPIView(ListAPIView):
    """
    Assignee : 기연

    GET : 게시글 목록 조회(검색)
    """
    
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer

    filter_backends = [DjangoFilterBackend, CustomSearchFilter, OrderingFilter]
    filterset_class = BoardFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'likecounts', 'viewcounts', 'sharecounts']
        

        

    
