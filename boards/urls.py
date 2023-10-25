from django.urls import path
from .views import BoardsListAPIView, BoardDetailView, AnalyticsView


urlpatterns = [
    path("", BoardsListAPIView.as_view(), name="boards-list"), # 게시글 목록 조회 API
    path("detail/<int:content_id>/", BoardDetailView.as_view(), name="board_detail"),
    path("analytics/", AnalyticsView.as_view()),
]
