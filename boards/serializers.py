from rest_framework import serializers
from .models import Board


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Board
        # fields = "__all__"
        fields = (
            "content_id",
            "owner",
            "title",
            "feed_type",
            "content",
            "hashtags",
            "viewcounts",
            "likecounts",
            "sharecounts",
            "created_at",
            "updated_at",
        )
