from rest_framework import serializers
from .models import Board


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

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
    
    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y년 %m월 %d일 %H시 %M분")
        return None

    def get_updated_at(self, obj):
        if obj.updated_at:
            return obj.updated_at.strftime("%Y년 %m월 %d일 %H시 %M분")
        return None


class BoardListSerializer(serializers.ModelSerializer):
    """
    Assignee : 기연
    """

    owner = serializers.StringRelatedField(read_only=True)
    liked_users = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Board
        fields = "__all__"


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = "__all__"
