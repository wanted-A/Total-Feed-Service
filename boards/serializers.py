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

class BoardListSerializer(serializers.ModelSerializer):
    """
    Assignee : 기연
    """

    class Meta:
        model = Board
        fields = "__all__"
      
      
class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

