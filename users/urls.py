# from django.urls import path
# from .views import UserCreateView, LoginView, LogoutView

# urlpatterns = [
#     path("register/", UserCreateView.as_view(), name="register"),
#     path("login/", LoginView.as_view(), name="login"),
#     path("logout/", LogoutView.as_view(), name="logout"),
# ]

from django.urls import path
from .views import ResgisterView, LogoutView ,LoginView, VerifyEmail
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path("register/", ResgisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("verify/<str:token>",VerifyEmail.as_view()),
]
