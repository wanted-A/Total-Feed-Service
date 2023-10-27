from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Board
from .serializers import BoardSerializer, BoardListSerializer
from .filters import BoardFilter, CustomSearchFilter

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import datetime, timedelta


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
    search_fields = ["title", "content"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "likecounts",
        "viewcounts",
        "sharecounts",
    ]


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


# api/v1/boards/analytics/?query_params
class AnalyticsView(APIView):
    # 사용자 인증 관련 기능 완성시 아래 주석 해제할 것
    # permission_classes = [permissions.IsAuthenticated]

    # Swagger를 활용한 API 문서 작성을 위한 변수(query_)
    query_hashtag = openapi.Parameter(
        "hashtag", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="검색할 해시태그"
    )
    query_type = openapi.Parameter(
        "type",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="통계 범위 조건(date: 일별 통계 / hour: 시간별 통계)",
        required=True,
        default="date",
    )
    query_start = openapi.Parameter(
        "start",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="통계 시작일(YYYY-MM-DD), 미입력시 오늘로부터 7일전 날짜로 설정",
        default=datetime.strftime(datetime.now() - timedelta(days=7), "%Y-%m-%d"),
    )
    query_end = openapi.Parameter(
        "end",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="통계 종료일(YYYY-MM-DD), 미입력시 오늘 날짜로 설정",
        default=datetime.strftime(datetime.now(), "%Y-%m-%d"),
    )
    query_value = openapi.Parameter(
        "value",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="통계 항목(count: 게시물 갯수 / view_count: 게시물 조회수 합계 / like_count: 게시물 좋아요수 합계 / share_count: 게시물 공유수 합계)",
        default="count",
    )

    # Swagger를 활용한 API 문서 작성을 위한 데코레이터
    @swagger_auto_schema(
        operation_id="통계",
        operation_description="게시물에 대한 통계를 제공합니다.",
        manual_parameters=[
            query_hashtag,
            query_type,
            query_start,
            query_end,
            query_value,
        ],
        responses={
            200: "{'result': { 'YYYY-MM-DD': 10, 'YYYY-MM-DD': 11 }}\n{'result': { 'YYYY-MM-DD HH:MM:SS': 10, 'YYYY-MM-DD HH:MM:SS': 11 }}"
        },
    )
    def get(self, request):
        hashtag = request.query_params.get("hashtag", request.user)
        hashtag = Hashtag.objects.get(tag=hashtag)

        search_type = request.query_params.get("type", "date")

        # 쿼리 파라미터에 종료일이 명시되지 않으면 오늘 날짜로 설정
        end = (
            datetime.strptime(request.query_params.get("end"), "%Y-%m-%d")
            if request.query_params.get("end") is not None
            else datetime.now()
        )
        # 종료일의 23시 59분 59초로 설정
        end = end.replace(hour=23, minute=59, second=59)

        # 쿼리 파라미터에 시작일이 명시되지 않으면 오늘로부터 7일 전 날짜로 설정
        start = (
            datetime.strptime(request.query_params.get("start"), "%Y-%m-%d")
            if request.query_params.get("start") is not None
            else datetime.now() - timedelta(days=7)
        )

        # 날짜 기준 통계를 요청받았을 때, 최대 30일 까지만 조회 가능
        if (search_type == "date") and (end - start > timedelta(days=30)):
            start = datetime.now() - timedelta(days=30)
        # 시간 기준 통계를 요청받았을 때, 최대 7일 까지만 조회 가능
        elif (search_type == "hour") and (end - start > timedelta(days=7)):
            start = datetime.now() - timedelta(days=7)

        # 시작일의 0시 0분 0초 0밀리초로 설정
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        value = request.query_params.get("value", "count")

        result = {}
        if value == "count":
            # 날짜 기준 게시물 갯수 반환
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(board_count=Coalesce(Count("title"), 0))

                    start += timedelta(days=1)
            # 시간 기준 게시물 갯수 반환
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        board_count=Coalesce(Count("title"), 0)
                    )

                    start += timedelta(hours=1)
        elif value == "view_count":
            # 날짜 기준 조회수 합계 반환
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_likes=Coalesce(Sum("viewcounts"), 0))

                    start += timedelta(days=1)
            # 시간 기준 조회수 합계 반환
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_likes=Coalesce(Sum("viewcounts"), 0)
                    )

                    start += timedelta(hours=1)
        elif value == "like_count":
            # 날짜 기준 좋아요수 합계 반환
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_likes=Coalesce(Sum("likecounts"), 0))

                    start += timedelta(days=1)
            # 시간 기준 좋아요수 합계 반환
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_likes=Coalesce(Sum("likecounts"), 0)
                    )

                    start += timedelta(hours=1)
        else:
            # 날짜 기준 공유수 합계 반환
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_shares=Coalesce(Sum("sharecounts"), 0))

                    start += timedelta(days=1)
            # 시간 기준 공유수 합계 반환
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags=hashtag.id,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_shares=Coalesce(Sum("sharecounts"), 0)
                    )

                    start += timedelta(hours=1)

        return Response({"result": result}, status=status.HTTP_200_OK)
