from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # UserSerializer에서 정의한 비밀번호 유효성 검사 로직을 재사용
        return UserSerializer().validate_password(value)


# class ChangePasswordView(APIView):
#     """
#     비밀번호 변경 API

#     PATCH: 현재 사용자의 비밀번호를 변경합니다.
#     """

#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         user = request.user
#         old_password = serializer.validated_data.get("old_password")
#         new_password = serializer.validated_data.get("new_password")

#         # 기존 비밀번호가 올바른지 확인
#         if not user.check_password(old_password):
#             return Response(
#                 {"detail": "Old password is incorrect."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # 새로운 비밀번호가 이전 비밀번호와 동일한지 확인
#         if user.check_password(new_password):
#             return Response(
#                 {"detail": "새 비밀번호는 이전 비밀번호와 달라야 합니다."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # 비밀번호 변경 - 재사용 확인 로직
#         user.check_previous_passwords(new_password)
#         user.save()

#         return Response(
#             {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
#         )


class LogoutView(APIView):

    """
    로그아웃 API

    POST: 로그아웃하고 현재 토큰을 블랙리스트에 추가합니다.
    """

    # permission_classes = [AllowAny]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # print(request.headers)
        try:
            # 현재 요청의 사용자의 refresh token을 가져옵니다.
            refresh_token = (
                request.auth
            )  # Assuming this is the refresh token sent by the user.
            token = RefreshToken(refresh_token)

            # 토큰을 블랙리스트에 추가합니다.
            token.blacklist()

            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserView(APIView):
    """
    사용자 정보 API
    회원가입

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
            # UserSerializer의 create 메서드를 호출하여 새 사용자를 생성
            user = serializer.save()
            # 새 사용자가 생성된 후 토큰을 생성
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
