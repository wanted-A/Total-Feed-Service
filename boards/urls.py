from django.urls import path

from boards.views import BoardsListAPIView

urlpatterns = [
    path("", BoardsListAPIView.as_view(), name="boards-list"), # 게시글 목록 조회 API
]
