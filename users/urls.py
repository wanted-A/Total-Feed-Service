# from django.urls import path
# from .views import UserCreateView, LoginView, LogoutView

# urlpatterns = [
#     path("register/", UserCreateView.as_view(), name="register"),
#     path("login/", LoginView.as_view(), name="login"),
#     path("logout/", LogoutView.as_view(), name="logout"),
# ]

from django.urls import path
from .views import ResgisterView, LogoutView ,LoginView

urlpatterns = [
    path("register/", ResgisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
