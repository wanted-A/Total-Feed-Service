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
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import datetime, timedelta


# api/v1/boards/write/
class BoardWriteView(APIView):
    # board 작성 view

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {"message : title, feed_type, content(선택), hashtags(선택) 를 입력해주세요."},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = BoardSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


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


# api/v1/boards/<int:content_id>/
class BoardDetailView(APIView):
    """
    GET : 게시글 상세 조회
    POST : 게시글 좋아요(좋아요 취소 기능 포함)
    PUT : 게시글 수정
    DELETE : 게시글 삭제
    """

    def get_object(self, content_id):
        try:
            return Board.objects.get(content_id=content_id)
        except Board.DoesNotExist:
            raise NotFound("해당 게시물을 찾을 수 없습니다.")

    def get(self, request, content_id):
        board = self.get_object(content_id)
        board.viewcounts += 1
        board.save()
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, content_id):
        board = self.get_object(content_id)
        user = request.user

        if user.is_anonymous:
            raise PermissionDenied("로그인이 필요합니다.")

        if board.owner.id == user.id:
            raise PermissionDenied("자신의 게시물은 좋아요를 누를 수 없습니다.")

        # 좋아요 한번만 누르기(좋아요 취소 기능)
        if board.liked_users.filter(id=user.id).exists():
            board.liked_users.remove(user)
            board.likecounts -= 1
            board.save()
            message = "좋아요 취소"
        else:
            board.liked_users.add(user)
            board.likecounts += 1
            board.save()
            message = "좋아요"

        return Response({"message": message}, status=status.HTTP_200_OK)

        # 좋아요 무제한 기능(한명이 무제한으로 다른 사람꺼 누르기 가능)
        # board.likecounts += 1
        # board.save()
        # message = "좋아요"

        # return Response({"message": message, "total_likes":board.likecounts}, status=status.HTTP_200_OK)

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


# api/v1/boards/<str:feed_type>/likes/<int:content_id>/
class BoardLikesView(APIView):
    """
    api 호출 시 좋아요 증가(무제한)
    """

    # 수정 할 부분
    def get_feed_type(self, feed_type):
        try:
            return Board.FeedChoices(feed_type)
        except ValueError:
            raise NotFound("해당 피드 타입을 찾을 수 없습니다.")
    
    # -> feed_typed 을 불러와서 endpoint로 사용하기

    def get_content(self, content_id, feed_type):
        try:
            return Board.objects.get(content_id=content_id, feed_type=feed_type)
        except Board.DoesNotExist:
            raise NotFound("해당 게시물을 찾을 수 없습니다.")

    def get(self, request, feed_type, content_id):
        try:
            board = Board.objects.get(feed_type=feed_type, content_id=content_id)
        except Board.DoesNotExist:
            raise NotFound("해당 게시물을 찾을 수 없습니다.")

        user = request.user
        if user.is_anonymous:
            raise PermissionDenied("로그인이 필요합니다.")

        # 조회 시 좋아요 수 증가
        board.likecounts += 1
        board.liked_users.add(user)

        likes = board.liked_users.all()
        like_users = [{"username": user.username} for user in likes]

        board.save()

        response_data = {
            "owner": board.owner.username,
            "feed_type": board.feed_type,
            "title": board.title,
            "content": board.content,
            "like_users": like_users,
            "like_count": board.likecounts,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# api/v1/boards/analytics/?query_params
class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    )
    def get(self, request):
        hashtag = request.query_params.get("hashtag", request.user)
        search_type = request.query_params.get("type", "date")

        end = (
            datetime.strptime(request.query_params.get("end"), "%Y-%m-%d")
            if request.query_params.get("end") is not None
            else datetime.now()
        )
        end = end.replace(hour=23, minute=59, second=59)

        start = (
            datetime.strptime(request.query_params.get("start"), "%Y-%m-%d")
            if request.query_params.get("start") is not None
            else datetime.now() - timedelta(days=7)
        )
        start = (
            datetime.now() - timedelta(days=7)
            if (end - start) > timedelta(days=7)
            else start
        )
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        value = request.query_params.get("value", "count")

        result = {}
        if value == "count":
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(board_count=Count("title"))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        board_count=Count("title")
                    )

                    start += timedelta(hours=1)
        elif value == "view_count":
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_likes=Sum("viewcounts"))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_likes=Sum("viewcounts")
                    )

                    start += timedelta(hours=1)
        elif value == "like_count":
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_likes=Sum("likecounts"))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_likes=Sum("likecounts")
                    )

                    start += timedelta(hours=1)
        else:
            if search_type == "date":
                while start <= end:
                    result[datetime.strftime(start, "%Y-%m-%d")] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[
                            start,
                            start.replace(hour=23, minute=59, second=59),
                        ],
                    ).aggregate(total_shares=Sum("sharecounts"))

                    start += timedelta(days=1)
            else:
                while start <= end:
                    result[
                        datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
                    ] = Board.objects.filter(
                        hashtags__icontains=hashtag,
                        created_at__range=[start, start.replace(minute=59, second=59)],
                    ).aggregate(
                        total_shares=Sum("sharecounts")
                    )

                    start += timedelta(hours=1)

        return Response({"result": result, "status": status.HTTP_200_OK})
