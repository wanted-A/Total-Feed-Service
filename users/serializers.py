from rest_framework import serializers
from .models import User
import re


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_password(self, value):
        # 비밀번호 복잡성 검증 로직.
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자리 이상이어야 합니다.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 대문자를 포함해야 합니다.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 소문자를 포함해야 합니다.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 숫자를 포함해야 합니다.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 특수문자를 포함해야 합니다.")
        return value

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user
