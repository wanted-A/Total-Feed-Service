from rest_framework import serializers
from .models import Board


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

