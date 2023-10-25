from rest_framework.serializers import ModelSerializer

from boards.models import Board

class BoardListSerializer(ModelSerializer):
    """
    Assignee : 기연
    """

    class Meta:
        model = Board
        fields = "__all__"