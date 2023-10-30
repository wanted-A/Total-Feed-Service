from django.urls import path
from .views import BoardShareAPIView, BoardListAPIView, BoardDetailView, AnalyticsView, BoardWriteView, BoardLikesView


urlpatterns = [
    path("", BoardListAPIView.as_view(), name="boards-list"), # 게시글 목록 조회 API
    path("write/", BoardWriteView.as_view(), name="board-write"), # 게시글 작성 API
    path("<int:content_id>/", BoardDetailView.as_view(), name="board-detail"), # 게시글 상세 조회 API
    path("<str:feed_type>/likes/<int:content_id>/", BoardLikesView.as_view(), name="board-likes"), # 게시글 작성 API
    path("share/<int:content_id>/", BoardShareAPIView.as_view(), name="board-share"),
    path("analytics/", AnalyticsView.as_view()),
]