# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from rest_framework_simplejwt.tokens import RefreshToken


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ("id", "username", "password")
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         user = get_user_model().objects.create_user(
#             username=validated_data["username"], password=validated_data["password"]
#         )
#         return user


# class TokenObtainPairSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)
#     tokens = serializers.SerializerMethodField()

#     def get_tokens(self, obj):
#         user = self.context["request"].user
#         refresh = RefreshToken.for_user(user)
#         return {
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#         }


from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_password(self, value):
        # 비밀번호 복잡성 검증 로직.
        if len(value) < 10:
            raise serializers.ValidationError("비밀번호는 최소 10자리 이상이어야 합니다.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 대문자를 포함해야 합니다.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 소문자를 포함해야 합니다.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 숫자를 포함해야 합니다.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("비밀번호는 최소 한 개의 특수문자를 포함해야 합니다.")

        # 흔한 비밀번호 적용 시 에러 표시
        common_passwords = [
            "123456",
            "password",
            "123456789",
            "12345",
            "12345678",
            "qwerty",
            "1234567",
            "111111",
            "1234567890",
            "123123",
            "abc123",
            "1234",
            "password1",
            "iloveyou",
            "1q2w3e4r",
            "000000",
            "qwerty123",
            "zaq12wsx",
            "dragon",
            "sunshine",
            "princess",
            "letmein",
            "654321",
            "monkey",
            "27653",
            "1qaz2wsx",
            "123321",
            "qwertyuiop",
            "superman",
            "asdfghjkl",
        ]
        if value in common_passwords:
            raise serializers.ValidationError("이미 유출된 비밀번호입니다. 다른 비밀번호를 선택하세요.")

        return value

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user
