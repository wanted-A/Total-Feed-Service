from django.contrib import admin
from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        "content_id",
        "owner",
        "title",
        "feed_type",
    )

    list_display_links = (
        "content_id",
        "owner",
        "title",
        "feed_type",
    )
    
    search_fields = ("title", "feed_type", "user__username")