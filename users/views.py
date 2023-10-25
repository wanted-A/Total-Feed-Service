from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import serializers

from .models import User
from .serializers import UserSerializer


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # UserSerializer에서 정의한 비밀번호 유효성 검사 로직을 재사용
        return UserSerializer().validate_password(value)


class ChangePasswordView(APIView):
    """
    비밀번호 변경 API

    PATCH: 현재 사용자의 비밀번호를 변경합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")

        # 기존 비밀번호가 올바른지 확인
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새로운 비밀번호가 이전 비밀번호와 동일한지 확인
        if user.check_password(new_password):
            return Response(
                {"detail": "새 비밀번호는 이전 비밀번호와 달라야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class UserView(APIView):
    """
    사용자 정보 API

    GET: 등록된 사용자 중 최근 10명의 목록을 반환합니다.
    POST: 새로운 사용자를 생성합니다.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = User.objects.all()[:10]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    비밀번호 변경 API

    PATCH: 현재 사용자의 비밀번호를 변경합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # 기존 비밀번호가 올바른지 확인
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새로운 비밀번호가 이전 비밀번호와 동일한지 확인
        if user.check_previous_password(new_password):
            return Response(
                {
                    "detail": "New password should be different from the previous password."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )
