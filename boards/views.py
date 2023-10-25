from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from datetime import datetime, timedelta
from django.db.models import Count, Sum

from .models import Board
from .serializers import BoardListSerializer
from boards.filters import BoardFilter, CustomSearchFilter


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
        

class AnalyticsView(APIView):
    def get(self, request):
        hashtag = request.query_params.get('hashtag', request.user)
        search_type = request.query_params.get('type', 'date')

        end = datetime.strptime(request.query_params.get(
            'end'), '%Y-%m-%d') if request.query_params.get('end') is not None else datetime.now()
        end = end.replace(hour=23, minute=59, second=59)

        start = datetime.strptime(request.query_params.get(
            'start'), '%Y-%m-%d') if request.query_params.get('start') is not None else datetime.now() - timedelta(days=7)
        start = datetime.now() - timedelta(days=7) if (end -
                                                       start) > timedelta(days=7) else start
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        value = request.query_params.get('value', 'count')

        result = {}
        if value == 'count':
            if search_type == 'date':
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(
                            hour=23, minute=59, second=59)]
                    ).aggregate(board_count=Count('title'))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d %H:%M:%S')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start, start.replace(minute=59, second=59)]
                    ).aggregate(board_count=Count('title'))

                    start += timedelta(hours=1)
        elif value == 'view_count':
            if search_type == 'date':
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(
                            hour=23, minute=59, second=59)]
                    ).aggregate(total_likes=Sum('viewcounts'))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d %H:%M:%S')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start, start.replace(minute=59, second=59)]
                    ).aggregate(total_likes=Sum('viewcounts'))

                    start += timedelta(hours=1)
        elif value == 'like_count':
            if search_type == 'date':
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(
                            hour=23, minute=59, second=59)]
                    ).aggregate(total_likes=Sum('likecounts'))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d %H:%M:%S')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start, start.replace(minute=59, second=59)]
                    ).aggregate(total_likes=Sum('likecounts'))

                    start += timedelta(hours=1)
        else:
            if search_type == 'date':
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(
                            hour=23, minute=59, second=59)]
                    ).aggregate(total_shares=Sum('sharecounts'))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[datetime.strftime(start, '%Y-%m-%d %H:%M:%S')] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start, start.replace(minute=59, second=59)]
                    ).aggregate(total_shares=Sum('sharecounts'))

                    start += timedelta(hours=1)

        return Response({'result': result}, status=status.HTTP_200_OK)
