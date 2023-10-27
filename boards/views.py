from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from boards.pagination import CustomPageNumberPagination

from .models import Board, Hashtag
from .serializers import BoardSerializer, BoardListSerializer

from django.db.models import Count, Sum

from datetime import datetime, timedelta
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# api/v1/boards/?query_params
class BoardsListAPIView(APIView):
    """
    Assignee : 기연
    
    게시글 목록 조회 및 검색 기능
    """
    permission_classes = [permissions.IsAuthenticated]

    query_hashtag = openapi.Parameter(
        "hashtag", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="검색할 해시태그"
    )
    query_type = openapi.Parameter(
        "type", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="검색할 feed type"
    )
    query_order_by = openapi.Parameter(
        "order_by", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="정렬 기준", default="created_at"
    )
    query_search_by = openapi.Parameter(
        "search_by", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="검색기준", default="title,content"
    )
    query_search = openapi.Parameter(
        "search", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="검색 키워드"
    )
    query_page = openapi.Parameter(
        "page", openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="페이지번호"
    )
    query_page_count = openapi.Parameter(
        "page_count", openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="페이지당 게시글 갯수"
    )

    @swagger_auto_schema(
        operation_id="게시글 목록 검색",
        operation_description="검색/정렬 기준에 대한 게시글 목록을 조회합니다.",
        manual_parameters=[
            query_hashtag,
            query_type,
            query_order_by,
            query_search_by,
            query_search,
            query_page,
            query_page_count
        ],
    )
    def get(self, request):
        hashtag = request.query_params.get('hashtag', request.user) # 태그 검색 키워드 / defalut : 본인계정
        type = request.query_params.get('type', '') # feed_type : facebook, instagram, etc.
        order_by = request.query_params.get('order_by', 'created_at') # 정렬 기준
        search_by = request.query_params.get('search_by', 'title,content') # 키워드 검색 기준(title, content, title+content)
        search = request.query_params.get('search', '') # 검색 키워드

        query = Q()
        
        # hashtag
        hashtag_instance = Hashtag.objects.get(tag__exact=hashtag)
        queryset = hashtag_instance.tagging.all()

        # type
        if type: query |= Q(feed_type=type)

        # search
        if search:
            if search_by == 'title':
                query |= Q(title__contains=search)
            elif search_by == 'content':
                query |= Q(content__contains=search)
            else:
                query |= (Q(title__contains=search) & Q(content__contains=search))
        
        queryset = queryset.filter(query).order_by(order_by)

        # 페이지네이션 적용
        paginator = CustomPageNumberPagination()
        paginated_data = paginator.paginate_queryset(queryset=queryset, request=request)

        serializer = BoardListSerializer(paginated_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class BoardDetailView(APIView):
    # board 상세 조회 view

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, content_id):
        try:
            return Board.objects.get(content_id=content_id)
        except Board.DoesNotExist:
            raise NotFound("해당 게시물을 찾을 수 없습니다.")

    def get(self, request, content_id):
        board = self.get_object(content_id)
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, content_id):
        board = self.get_object(content_id)

        if board.owner.id != request.user.id:
            raise PermissionDenied("해당 게시물의 작성자가 아닙니다.")

        serializer = BoardSerializer(
            board,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotFound("해당 게시물을 찾을 수 없습니다.")

    def delete(self, request, content_id):
        board = self.get_object(content_id)

        if board.owner.id != request.user.id:
            raise PermissionDenied("해당 게시물의 작성자가 아닙니다.")

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
