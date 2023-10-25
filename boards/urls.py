from django.urls import path
from .views import BoardsListAPIView, AnalyticsView

urlpatterns = [
    path("", BoardsListAPIView.as_view(), name="boards-list"), # 게시글 목록 조회 API
    path("analytics/", AnalyticsView.as_view()),
]