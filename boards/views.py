from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Board
from .serializers import BoardSerializer, BoardListSerializer
from boards.filters import BoardFilter, CustomSearchFilter

from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend

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


# api/v1/boards/detail/<int:content_id>/
class BoardDetailView(APIView):
    # board 상세 조회 view

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

        return Response({"result": result}, status=status.HTTP_200_OK)
