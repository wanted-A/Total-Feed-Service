from django.urls import path
from .views import BoardsListAPIView, BoardDetailView, AnalyticsView, BoardWriteView, BoardLikesView


urlpatterns = [
    path("", BoardsListAPIView.as_view(), name="boards-list"), # 게시글 목록 조회 API
    path("write/", BoardWriteView.as_view(), name="board-write"), # 게시글 작성 API
    path("<str:feed_type>/likes/<int:content_id>/", BoardLikesView.as_view(), name="board-likes"), # 게시글 작성 API
    path("<int:content_id>/", BoardDetailView.as_view(), name="board-detail"), # 게시글 상세 조회 API
    path("analytics/", AnalyticsView.as_view()),
]