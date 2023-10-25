from django.urls import path

from . import views

urlpatterns = [
    # path("new/", views.BoardNewContentView.as_view(), name="board_new_content"),
    path("detail/<int:content_id>/", views.BoardDetailView.as_view(), name="board_detail"),
]
