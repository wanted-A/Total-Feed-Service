import re
import environ

env = environ.Env()

from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
)
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail


# api/v1/users/register/
class ResgisterView(APIView):
    """
    회원가입
    POST: 새로운 사용자를 생성합니다.
    """

    permission_classes = [permissions.AllowAny]

    # def get(self, request):
    #     users = User.objects.all()[:10]
    #     serializer = UserSerializer(users, many=True)
    #     return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # UserSerializer의 create 메서드를 호출하여 새 사용자를 생성
            user = serializer.save()

            # # 새 사용자가 생성된 후 토큰을 생성
            # token, created = Token.objects.get_or_create(user=user)

            # jwt 토큰 접근
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            # 이메일 인증메일 보내기
            current_site = "127.0.0.1:8000"
            link = "http://" + current_site + "/api/v1/users/verify/" + str(refresh)
            email_subject = "이메일 인증을 완료해주세요."
            email_body = (
                "안녕하세요. " + user.username + "님, \n 아래 링크를 클릭하시면 이메일 인증이 완료됩니다.\n" + link
            )

            send_mail(
                email_subject,
                email_body,
                env("EMAIL_HOST_USER"),
                [user.email],
            )

            return Response(
                {
                    "username": user.username,
                    "message": "이메일을 인증하여 회원가입을 완료해주세요.",
                    "token": {"refresh": refresh_token, "access": access_token},
                },
                status=status.HTTP_201_CREATED,
            )

            # return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# api/v1/users/login/
class LoginView(APIView):
    """
    로그인 API
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response(
                {"message": "아이디와 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)

            # jwt 토큰 접근해서 인증 요청
            token = CustomTokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {"message": "로그인 성공", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

            # 세션에 refresh_token 저장
            request.session["refresh"] = refresh_token
            # 쿠키에 access_token 저장
            res.set_cookie("access", access_token, httponly=True)

            return res
        else:
            return Response({"message": "아이디 혹은 비밀번호가 틀립니다."})


# api/v1/users/logout/
class LogoutView(APIView):
    """
    로그아웃 API

    POST: 로그아웃하고 현재 토큰을 블랙리스트에 추가합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        try:
            # 현재 요청의 사용자의 refresh token을 가져옵니다.
            refresh_token = (
                request.auth
            )  # Assuming this is the refresh token sent by the user.
            token = RefreshToken(refresh_token)

            # 토큰을 블랙리스트에 추가합니다.
            token.blacklist()

            request.session.flush()

            res = Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
            res.delete_cookie("access")

            return res
        except TokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token["user_id"])

            if not user.is_approved:
                user.is_approved = True
                user.save()
                return Response(
                    {"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "이미 인증된 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST
                )

        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response(
                {"message": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST
            )


# class CustomLoginView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer


# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)

#     def validate_new_password(self, value):
#         # UserSerializer에서 정의한 비밀번호 유효성 검사 로직을 재사용
#         return UserSerializer().validate_password(value)


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
