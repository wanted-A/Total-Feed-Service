from rest_framework import serializers
from .models import Board, Hashtag


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        queryset=Hashtag.objects.all(),
        slug_field="tag",
    )

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

    hashtags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Board
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

    def to_representation(self, instance):
        # content 최대 20자 까지만 표현
        res = super().to_representation(instance)
        res.update({"content": res["content"][:20]})
        return res


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = "__all__"
